"""SAGIP skimmer boat: Autodesk Fusion script (Python), detailed and colored.

Builds the planning model as separate, named, colored bodies. Body names start with the part
number in the prototype parts table (1 to 12, "ctx_" for context such as the river bank).
All sizes are planning values in millimetres. Edit the PARAMETERS block and run again.
Running it again first deletes the bodies this script made earlier, so nothing doubles up.

How to run:
  1. In Fusion open a new Part Design (units mm). Save it first.
  2. Utilities > Add-Ins > Scripts and Add-Ins, then the arrow next to the green +,
     Create new script or add-in, Python, Script, name it SAGIP_Boat.
  3. Paste this whole file over the generated SAGIP_Boat.py, save, select it and click Run.
"""
import math
import re
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
INCLUDE_FLOOD_NODE = True        # bank, staff gauge and node box (context)
COLOR = True                     # set False to skip colors

MM = 0.1  # Fusion works in centimetres

# first keyword found in a body name wins, so more specific names come first
COLORS = [
    ('Float_Switch', (214, 40, 40)), ('Cap', (196, 98, 22)), ('Float_', (240, 132, 40)),
    ('Belt_Rail', (160, 165, 172)), ('Belt', (45, 45, 52)), ('Cleat', (15, 15, 18)),
    ('Roller', (170, 174, 180)), ('Motor', (210, 170, 60)), ('Coupling', (120, 124, 130)),
    ('Clamp', (160, 165, 172)), ('Strap', (160, 165, 172)), ('Panel_Leg', (160, 165, 172)),
    ('Deck', (209, 168, 107)), ('Panel_Frame', (200, 204, 210)),
    ('Solar_Panel', (20, 50, 115)), ('Node_Solar', (20, 50, 115)),
    ('Electronics_Box', (200, 204, 208)), ('Electronics_Lid', (225, 228, 232)),
    ('Node_Box', (200, 204, 208)), ('Latch', (50, 50, 56)), ('Gland', (20, 20, 22)),
    ('Antenna', (20, 20, 22)), ('Battery_Strap', (60, 60, 66)), ('Battery_Terminal', (214, 40, 40)),
    ('Battery', (140, 30, 30)), ('Fuse', (214, 40, 40)), ('Buck', (30, 90, 170)),
    ('Thruster_Prop', (240, 200, 40)), ('Thruster_Hub', (240, 200, 40)),
    ('Thruster', (45, 45, 52)), ('Mount_Arm', (160, 165, 172)),
    ('Side_Ultrasonic', (30, 140, 70)), ('Sensor_Back', (60, 60, 66)), ('Compass', (30, 140, 70)),
    ('LED_Strip', (250, 240, 200)), ('S3_Board', (30, 140, 70)), ('Hood', (22, 22, 26)),
    ('Scoop', (190, 195, 202)), ('Servo_Horn', (230, 230, 230)), ('Gate_Servo', (40, 60, 150)),
    ('Gate_Flap', (240, 132, 40)), ('Bin_A', (50, 115, 205)), ('Bin_B', (64, 166, 90)),
    ('Bow_Camera_Lens', (10, 10, 12)), ('Bow_Camera', (30, 30, 36)), ('Bow_Post', (160, 165, 172)),
    ('Sun_Shield', (60, 60, 66)), ('Bump', (214, 40, 40)), ('Bank', (115, 140, 82)),
    ('Staff_Gauge', (245, 245, 245)), ('Gauge_Band', (214, 40, 40)), ('Buzzer', (25, 25, 28)),
    ('Node_LED', (230, 60, 60)),
]


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

        # direct modelling lets us add bodies freely, otherwise use one base feature
        try:
            design.designType = adsk.fusion.DesignTypes.DirectDesignType
        except Exception:
            pass

        # remove bodies from an earlier run of this script
        old = [b for b in root.bRepBodies if re.match(r'^(\d\d_|ctx_)', b.name)]
        for b in old:
            try:
                b.deleteMe()
            except Exception:
                pass

        base = None
        if design.designType == adsk.fusion.DesignTypes.ParametricDesignType:
            base = root.features.baseFeatures.add()
            base.startEdit()

        count = [0]

        def put(tmp, name, no):
            body = root.bRepBodies.add(tmp, base) if base else root.bRepBodies.add(tmp)
            body.name = ('%02d_' % no if no else 'ctx_') + name
            count[0] += 1
            return body

        def tbox(c, size, ax=(1, 0, 0), ay=(0, 1, 0)):
            obb = adsk.core.OrientedBoundingBox3D.create(
                pt(*c), vec(*ax), vec(*ay), size[0] * MM, size[1] * MM, size[2] * MM)
            return tbm.createBox(obb)

        def box(name, no, c, size, ax=(1, 0, 0), ay=(0, 1, 0)):
            """box centred at c (mm), size (along ax, along ay, along ax x ay)"""
            return put(tbox(c, size, ax, ay), name, no)

        def cyl(name, no, c, r, h, axis='x'):
            d = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
            p1 = pt(c[0] - d[0] * h / 2, c[1] - d[1] * h / 2, c[2] - d[2] * h / 2)
            p2 = pt(c[0] + d[0] * h / 2, c[1] + d[1] * h / 2, c[2] + d[2] * h / 2)
            return put(tbm.createCylinderOrCone(p1, r * MM, p2, r * MM), name, no)

        def open_bin(name, no, c, size, wall=6):
            """open-topped bin: outer box minus an inner box, bottom wall of `wall` mm"""
            outer = tbox(c, size)
            inner = tbox((c[0], c[1], c[2] + wall), (size[0] - 2 * wall, size[1] - 2 * wall, size[2]))
            try:
                tbm.booleanOperation(outer, inner, adsk.fusion.BooleanTypes.DifferenceBooleanType)
            except Exception:
                pass
            return put(outer, name, no)

        deck_top = DECK_Z + DECK[2]

        # ---------------------------------------------------------- 11 floats, caps, clamps, straps, deck
        for sgn, nm in ((-1, 'Float_L'), (1, 'Float_R')):
            y = sgn * FLOAT_Y
            cyl(nm, 11, (0, y, FLOAT_R), FLOAT_R, FLOAT_L, 'x')
            for xs, e in ((-1, 'Stern'), (1, 'Bow')):
                cyl(nm + '_Cap' + e, 11, (xs * (FLOAT_L / 2 + 4), y, FLOAT_R), FLOAT_R + 4, 8, 'x')
            for i, x in enumerate((-450, 0, 450)):
                box(nm + '_Clamp%d' % (i + 1), 11,
                    (x, y, 2 * FLOAT_R + (DECK_Z - 2 * FLOAT_R) / 2), (40, 50, DECK_Z - 2 * FLOAT_R))
                # stainless strap around the pipe, shown as a thin collar
                cyl(nm + '_Strap%d' % (i + 1), 11, (x, y, FLOAT_R), FLOAT_R + 3, 24, 'x')
        box('Deck', 11, (0, 0, DECK_Z + DECK[2] / 2), DECK)

        # ---------------------------------------------------------- 7 solar panel with frame and legs
        pz = deck_top + 12 + PANEL[2] / 2
        box('Solar_Panel_30W', 7, (-390, 0, pz), (PANEL[0] - 12, PANEL[1] - 12, PANEL[2] - 4))
        for sy in (-1, 1):
            box('Panel_Frame_Long', 7, (-390, sy * (PANEL[1] / 2 - 3), pz), (PANEL[0], 12, PANEL[2]))
        for sx in (-1, 1):
            box('Panel_Frame_Short', 7, (-390 + sx * (PANEL[0] / 2 - 3), 0, pz), (12, PANEL[1] - 12, PANEL[2]))
        for dx in (-270, 270):
            for dy in (-140, 140):
                box('Panel_Leg', 7, (-390 + dx, dy, deck_top + 6), (20, 20, 12))

        # ---------------------------------------------------------- 6 electronics box
        ec = (-250, 275, deck_top + 40)
        box('Electronics_Box_IP65', 6, ec, (220, 160, 80))
        box('Electronics_Lid', 6, (ec[0], ec[1], deck_top + 82), (226, 166, 6))
        for dx in (-60, 60):
            box('Latch', 6, (ec[0] + dx, ec[1] - 82, deck_top + 66), (24, 6, 22))
            cyl('Cable_Gland', 6, (ec[0] + dx, ec[1] + 88, deck_top + 40), 8, 16, 'y')
        cyl('Antenna_Wifi', 6, (ec[0] + 90, ec[1] - 50, deck_top + 85 + 60), 3, 120, 'z')

        # ---------------------------------------------------------- power parts on the deck
        box('Fuse_Holder', 6, (0, 300, deck_top + 14), (70, 35, 28))
        for i, x in enumerate((60, 120)):
            box('Buck_Converter%d' % (i + 1), 6, (x, 300, deck_top + 11), (50, 38, 22))

        # ---------------------------------------------------------- 8 battery low between the floats
        bc = (-120, 0, 128)
        box('Battery_12V_12Ah', 8, bc, (240, 150, 100))
        box('Battery_Strap', 8, (bc[0], bc[1], bc[2] + 52), (30, 160, 4))
        for sy in (-1, 1):
            cyl('Battery_Terminal', 8, (bc[0] + 90, sy * 45, bc[2] + 56), 7, 12, 'z')
        box('Battery_Tray', 8, (bc[0], 0, bc[2] - 54), (260, 170, 8))

        # ---------------------------------------------------------- 9 thrusters, mounts, props
        for sgn, nm in ((-1, 'L'), (1, 'R')):
            y = sgn * FLOAT_Y
            box('Mount_Arm_' + nm, 9, (-FLOAT_L / 2 - 30, y, WATERLINE), (60, 14, 14))
            cyl('Thruster_' + nm, 9, (-FLOAT_L / 2 - 55, y, WATERLINE), 28, 100, 'x')
            cyl('Thruster_Shroud_' + nm, 9, (-FLOAT_L / 2 - 110, y, WATERLINE), 42, 40, 'x')
            px = -FLOAT_L / 2 - 135
            cyl('Thruster_Hub_' + nm, 9, (px, y, WATERLINE), 9, 24, 'x')
            for k in range(3):
                t = math.radians(120 * k)
                ct, st = math.cos(t), math.sin(t)
                box('Thruster_Prop_%s%d' % (nm, k + 1), 9, (px, y + 24 * ct, WATERLINE + 24 * st),
                    (4, 40, 10), (1, 0, 0), (0, ct, st))

        # ---------------------------------------------------------- 10 side sensors (compass optional)
        for sgn, nm in ((-1, 'L'), (1, 'R')):
            yy = sgn * (FLOAT_Y + FLOAT_R + 11)
            cyl('Side_Ultrasonic_' + nm, 10, (300, yy, 130), 14, 22, 'y')
            cyl('Sensor_Back_' + nm, 10, (300, yy + sgn * 18, 130), 10, 18, 'y')
        if INCLUDE_COMPASS:
            box('Compass_Module', 10, (480, -250, deck_top + 4), (30, 30, 8))

        # bump switches on the float bows (front sensing)
        for sgn, nm in ((-1, 'L'), (1, 'R')):
            y = sgn * FLOAT_Y
            box('Bump_Switch_' + nm, 10, (FLOAT_L / 2 + 20, y, 80), (24, 16, 16))
            box('Bump_Lever_' + nm, 10, (FLOAT_L / 2 + 44, y - sgn * 6, 80), (36, 4, 10))

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
        for nm, lx in (('Low', -BELT_L / 2), ('Top', BELT_L / 2)):
            cyl('Roller_' + nm, 3, belt_c(lx, -6), 22, BELT_W + 10, 'y')
        # gear motor at the top roller, with a coupling to the shaft
        cyl('Coupling', 3, belt_c(BELT_L / 2, -6, BELT_W / 2 + 22), 9, 30, 'y')
        box('Gear_Motor', 3, belt_c(BELT_L / 2 - 10, -6, BELT_W / 2 + 70), (90, 60, 60), ax, ay)

        hx = BELT_L / 2 - 110
        box('Camera_Hood', 4, belt_c(hx, 82), (260, 250, 150), ax, ay)
        box('Hood_Lip', 4, belt_c(hx, 9), (266, 256, 10), ax, ay)
        box('LED_Strip', 4, belt_c(hx, 140), (200, 14, 3), ax, ay)
        box('S3_Board', 4, belt_c(hx, 150), (56, 28, 6), ax, ay)

        # ---------------------------------------------------------- 2 scoop with side walls
        a = math.radians(18)
        sax = (math.cos(a), 0, -math.sin(a))
        box('Scoop', 2, (BELT_LOW[0] + 70, 0, BELT_LOW[2] - 28), (170, 300, 6), sax, (0, 1, 0))
        for sy in (-1, 1):
            box('Scoop_Wall', 2, (BELT_LOW[0] + 70 + 20 * math.sin(a), sy * 147,
                                  BELT_LOW[2] - 28 + 20 * math.cos(a)), (170, 6, 40), sax, (0, 1, 0))

        # ---------------------------------------------------------- 5 gate servo, flap and open bins
        top_x = BELT_LOW[0] - BELT_L * c
        box('Gate_Servo', 5, (top_x + 10, 0, 372), (60, 40, 40))
        cyl('Servo_Horn', 5, (top_x + 10, 0, 395), 10, 6, 'z')
        g = math.radians(30)
        box('Gate_Flap', 5, (top_x + 10, 0, 335), (110, 6, 70), (math.cos(g), math.sin(g), 0), (-math.sin(g), math.cos(g), 0))
        open_bin('Bin_A_Plastic', 5, (110, -95, deck_top + 75), (150, 170, 150))
        open_bin('Bin_B_Plants_Unsure', 5, (110, 95, deck_top + 75), (150, 170, 150))

        # ---------------------------------------------------------- 1 bow camera on a post
        box('Bow_Post', 1, (690, 300, deck_top + 130), (20, 20, 260))
        b = math.radians(-12)
        bax = (math.cos(b), 0, -math.sin(b))
        box('Bow_Camera_ESP32CAM', 1, (700, 300, deck_top + 275), (60, 40, 32), bax, (0, 1, 0))
        cyl('Bow_Camera_Lens', 1, (700 + 33, 300, deck_top + 275 - 3), 9, 8, 'x')
        box('Sun_Shield', 1, (710, 300, deck_top + 275 + 22), (80, 56, 3), bax, (0, 1, 0))
        cyl('Antenna_Bow', 1, (688, 300, deck_top + 275 + 40), 2, 50, 'z')

        # ---------------------------------------------------------- 12 flood node (context)
        if INCLUDE_FLOOD_NODE:
            by = 1200
            box('Bank', 0, (200, by + 80, WATERLINE + 8), (1100, 440, 24))
            box('Staff_Gauge', 12, (200, by - 190, 280), (30, 12, 560))
            for k in range(5):
                box('Gauge_Band', 12, (200, by - 190 - 7, 25 + 100 * k), (31, 3, 50))
            for z, nm in ((150, 'Watch'), (240, 'Alert'), (330, 'Danger')):
                cyl('Float_Switch_' + nm, 12, (200, by - 204, z), 12, 16, 'y')
            nb = (200, by + 20, WATERLINE + 75)
            box('Node_Box_IP67', 12, nb, (170, 120, 110))
            cyl('Buzzer', 12, (nb[0] - 40, nb[1] - 67, nb[2] + 10), 12, 14, 'y')
            cyl('Node_LED', 12, (nb[0] + 40, nb[1] - 64, nb[2] + 10), 5, 8, 'y')
            k = math.radians(-25)
            box('Node_Solar_2W', 12, (200, by + 20, WATERLINE + 145), (150, 100, 6),
                (1, 0, 0), (0, math.cos(k), math.sin(k)))

        if base:
            base.finishEdit()

        # ---------------------------------------------------------- colors
        colored = 0
        if COLOR:
            try:
                library_base = None
                for lib in app.materialLibraries:
                    for ap in lib.appearances:
                        if ap.name.startswith('Paint - Enamel Glossy') and ap.appearanceProperties.itemById('opaque_albedo'):
                            library_base = ap
                            break
                    if library_base:
                        break
                if library_base:
                    cache = {}

                    def appearance(rgb):
                        if rgb not in cache:
                            nm = 'SAGIP_%02X%02X%02X' % rgb
                            ap = design.appearances.itemByName(nm)
                            if not ap:
                                ap = design.appearances.addByCopy(library_base, nm)
                                prop = adsk.core.ColorProperty.cast(ap.appearanceProperties.itemById('opaque_albedo'))
                                prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                            cache[rgb] = ap
                        return cache[rgb]

                    for body in root.bRepBodies:
                        if not re.match(r'^(\d\d_|ctx_)', body.name):
                            continue
                        nm = body.name[3:] if body.name.startswith('ctx_') is False else body.name[4:]
                        for key, rgb in COLORS:
                            if key in nm:
                                body.appearance = appearance(rgb)
                                colored += 1
                                break
            except Exception:
                colored = -1

        app.activeViewport.fit()
        note = ''
        if COLOR and colored <= 0:
            note = '\nColors could not be applied (the geometry is fine).'
        ui.messageBox('SAGIP boat built: %d bodies, %d colored.%s\n'
                      'Open the Bodies folder in the browser. Names start with part numbers 1 to 12.'
                      % (count[0], max(colored, 0), note))
    except Exception:
        if ui:
            ui.messageBox('Script failed:\n{}'.format(traceback.format_exc()))
