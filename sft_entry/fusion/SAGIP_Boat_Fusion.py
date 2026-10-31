"""SAGIP skimmer boat: Autodesk Fusion script (Python).

Builds the same planning model as build/make_3d_model.py as separate, named bodies.
Body names start with the part number in the prototype parts table (1 to 12).
All sizes are planning values in millimetres. Edit the PARAMETERS block and run again.

How to run:
  1. In Fusion open a new Part Design (units mm). Save it first.
  2. Utilities > Add-Ins > Scripts and Add-Ins, then the green + next to My Scripts,
     choose Python, name it SAGIP_Boat, and create it.
  3. Paste this whole file over the generated SAGIP_Boat.py, save, select it and click Run.
"""
import math
import traceback

import adsk.core
import adsk.fusion

# ---------------------------------------------------------------- PARAMETERS (mm)
FLOAT_R = 80            # 6-inch PVC pipe, about 160 mm outside diameter
FLOAT_L = 1500          # one 1.5 m pipe per float
FLOAT_Y = 320           # float centre line, left and right
WATERLINE = 96          # about 60 percent submerged at the planning load
DECK_Z = 190            # underside of the deck
DECK = (1400, 760, 6)
PANEL = (600, 350, 18)  # 30 W panel, flat on the deck
BELT_L, BELT_W, BELT_ANGLE = 600, 220, 24
BELT_LOW = (640.0, 0.0, 150.0)   # low (bow) end of the belt, in the water
INCLUDE_COMPASS = False          # dropped to save cost, set True to add it back
INCLUDE_FLOOD_NODE = True        # bank, staff gauge and node box (context only)

MM = 0.1  # Fusion works in centimetres


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Open a Fusion design first (Part Design).')
            return
        root = design.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()

        # Z-up or Y-up: keep the model upright whichever the user's setting is
        z_up = False
        try:
            z_up = (app.preferences.generalPreferences.defaultModelingOrientation
                    == adsk.core.DefaultModelingOrientations.ZUpModelingOrientation)
        except Exception:
            pass

        def mv(x, y, z):
            """model (x length, y width, z up) to Fusion axes"""
            return (x, y, z) if z_up else (x, z, -y)

        def pt(x, y, z):
            a, b, c = mv(x, y, z)
            return adsk.core.Point3D.create(a * MM, b * MM, c * MM)

        def vec(x, y, z):
            a, b, c = mv(x, y, z)
            v = adsk.core.Vector3D.create(a, b, c)
            v.normalize()
            return v

        # Direct modelling lets us add bodies freely. If the file is parametric, use one base feature.
        base = None
        try:
            design.designType = adsk.fusion.DesignTypes.DirectDesignType
        except Exception:
            pass
        if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
            base = root.features.baseFeatures.add()
            base.startEdit()

        count = [0]

        def put(tmp, name, no):
            body = root.bRepBodies.add(tmp, base) if base else root.bRepBodies.add(tmp)
            body.name = ('%02d_' % no if no else 'ctx_') + name
            count[0] += 1
            return body

        def box(name, no, c, size, ax=(1, 0, 0), ay=(0, 1, 0)):
            """box centred at c (mm), size (along ax, along ay, along ax x ay)"""
            obb = adsk.core.OrientedBoundingBox3D.create(
                pt(*c), vec(*ax), vec(*ay), size[0] * MM, size[1] * MM, size[2] * MM)
            return put(tbm.createBox(obb), name, no)

        def cyl(name, no, c, r, h, axis='x'):
            d = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
            p1 = pt(c[0] - d[0] * h / 2, c[1] - d[1] * h / 2, c[2] - d[2] * h / 2)
            p2 = pt(c[0] + d[0] * h / 2, c[1] + d[1] * h / 2, c[2] + d[2] * h / 2)
            return put(tbm.createCylinderOrCone(p1, r * MM, p2, r * MM), name, no)

        # ---------------------------------------------------------- 11 floats, caps, clamps, deck
        for sgn, nm in ((-1, 'Float_L'), (1, 'Float_R')):
            y = sgn * FLOAT_Y
            cyl(nm, 11, (0, y, FLOAT_R), FLOAT_R, FLOAT_L, 'x')
            for xs, e in ((-1, 'Stern'), (1, 'Bow')):
                cyl(nm + '_Cap' + e, 11, (xs * (FLOAT_L / 2 + 4), y, FLOAT_R), FLOAT_R + 4, 8, 'x')
            for i, x in enumerate((-450, 0, 450)):
                box(nm + '_Clamp%d' % (i + 1), 11,
                    (x, y, 2 * FLOAT_R + (DECK_Z - 2 * FLOAT_R) / 2), (40, 50, DECK_Z - 2 * FLOAT_R))
        box('Deck', 11, (0, 0, DECK_Z + DECK[2] / 2), DECK)
        deck_top = DECK_Z + DECK[2]

        # ---------------------------------------------------------- 7 solar panel
        pz = deck_top + 12 + PANEL[2] / 2
        box('Solar_Panel_30W', 7, (-390, 0, pz), PANEL)
        for dx in (-270, 270):
            for dy in (-140, 140):
                box('Panel_Leg', 7, (-390 + dx, dy, deck_top + 6), (20, 20, 12))

        # ---------------------------------------------------------- 6 electronics box, 8 battery
        box('Electronics_Box_IP65', 6, (-250, 275, deck_top + 40), (220, 160, 80))
        box('Electronics_Lid', 6, (-250, 275, deck_top + 82), (226, 166, 6))
        box('Battery_12V_12Ah', 8, (-120, 0, 128), (240, 150, 100))

        # ---------------------------------------------------------- 9 thrusters
        for sgn, nm in ((-1, 'L'), (1, 'R')):
            y = sgn * FLOAT_Y
            cyl('Thruster_' + nm, 9, (-FLOAT_L / 2 - 55, y, WATERLINE), 28, 100, 'x')
            cyl('Thruster_Shroud_' + nm, 9, (-FLOAT_L / 2 - 110, y, WATERLINE), 42, 40, 'x')

        # ---------------------------------------------------------- 10 side sensors (compass optional)
        for sgn, nm in ((-1, 'L'), (1, 'R')):
            cyl('Side_Ultrasonic_' + nm, 10, (300, sgn * (FLOAT_Y + FLOAT_R + 11), 130), 14, 22, 'y')
        if INCLUDE_COMPASS:
            box('Compass_Module', 10, (480, -250, deck_top + 4), (30, 30, 8))

        # ---------------------------------------------------------- 3 belt, 4 hood (belt frame)
        th = math.radians(BELT_ANGLE)
        c, s = math.cos(th), math.sin(th)
        ax = (-c, 0, s)          # along the belt, up toward the stern
        ay = (0, -1, 0)          # across the belt (sign chosen so the normal points up)
        # ax x ay = (s, 0, c): the upward normal of the belt surface
        o = (BELT_LOW[0] - BELT_L / 2 * c, 0.0, BELT_LOW[2] + BELT_L / 2 * s)   # belt centre

        def belt_c(lx, lz, ly=0.0):
            return (o[0] + lx * ax[0] + lz * s, o[1] + ly, o[2] + lx * ax[2] + lz * c)

        box('Belt', 3, belt_c(0, 0), (BELT_L, BELT_W, 14), ax, ay)
        for sy in (-1, 1):
            box('Belt_Rail', 3, belt_c(0, 18, sy * (BELT_W / 2 + 5)), (BELT_L, 10, 40), ax, ay)
        for i, lx in enumerate(range(-270, 300, 70)):
            box('Cleat%02d' % (i + 1), 3, belt_c(lx, 16), (6, BELT_W - 20, 18), ax, ay)
        box('Camera_Hood', 4, belt_c(BELT_L / 2 - 110, 82), (260, 250, 150), ax, ay)
        box('Hood_Lip', 4, belt_c(BELT_L / 2 - 110, 9), (266, 256, 10), ax, ay)

        # ---------------------------------------------------------- 2 scoop
        a = math.radians(18)
        box('Scoop', 2, (BELT_LOW[0] + 70, 0, BELT_LOW[2] - 28), (170, 300, 6),
            (math.cos(a), 0, -math.sin(a)), (0, 1, 0))

        # ---------------------------------------------------------- 5 gate servo and bins
        top_x = BELT_LOW[0] - BELT_L * c
        box('Gate_Servo', 5, (top_x + 10, 0, 372), (60, 40, 40))
        for y, nm in ((-95, 'Bin_A_Plastic'), (95, 'Bin_B_Plants_Unsure')):
            box(nm, 5, (110, y, deck_top + 75), (150, 170, 150))

        # ---------------------------------------------------------- 1 bow camera
        box('Bow_Post', 1, (690, 300, deck_top + 130), (20, 20, 260))
        b = math.radians(-12)
        box('Bow_Camera_ESP32CAM', 1, (700, 300, deck_top + 275), (60, 40, 32),
            (math.cos(b), 0, -math.sin(b)), (0, 1, 0))

        # ---------------------------------------------------------- 12 flood node (context)
        if INCLUDE_FLOOD_NODE:
            by = 1200
            box('Bank', 0, (200, by + 80, WATERLINE + 8), (1100, 440, 24))
            box('Staff_Gauge', 12, (200, by - 190, 280), (30, 12, 560))
            for z, nm in ((150, 'Watch'), (240, 'Alert'), (330, 'Danger')):
                cyl('Float_Switch_' + nm, 12, (200, by - 204, z), 12, 16, 'y')
            box('Node_Box_IP67', 12, (200, by + 20, WATERLINE + 75), (170, 120, 110))
            k = math.radians(-25)
            box('Node_Solar_2W', 12, (200, by + 20, WATERLINE + 145), (150, 100, 6),
                (1, 0, 0), (0, math.cos(k), math.sin(k)))

        if base:
            base.finishEdit()
        app.activeViewport.fit()
        ui.messageBox('SAGIP boat built: %d bodies. Look in the Bodies folder of the browser. '
                      'Names start with the part number 1 to 12.' % count[0])
    except Exception:
        if ui:
            ui.messageBox('Script failed:\n{}'.format(traceback.format_exc()))
