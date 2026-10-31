"""2D top-view render of the SAGIP model with the bank flood node (uses make_3d_model.py)."""
import sys
sys.argv_orig = list(sys.argv); sys.argv = [sys.argv[0], "--no-stl"]
from make_3d_model import *
W, H = 1500, 1500
top, px = render(make_view(-90, 89.9), W, H, margin=0.09)
if "--labels" in sys.argv_orig: label(top, px, {1: (-10, -90), 2: (60, -90), 3: (-30, -100), 4: (40, 100), 5: (-60, 100), 6: (-40, -90), 7: (0, 110), 9: (-60, -90),
                10: (50, -90), 11: (-140, -70), 12: (120, -90)}, rad=24)
from PIL import Image as _I
c = _I.new('RGB', (W, H + 110), (255, 255, 255)); c.paste(top, (0, 110))
d = ImageDraw.Draw(c)
d.text((30, 20), 'SAGIP top view', fill=(11, 93, 143), font=font(40))
d.text((30, 70), 'Boat and bank flood node, rendered from above from the 3D model (planning sizes)', fill=(60, 60, 60), font=font(22, False))
c = c.crop((0,0,W,H+110)); c = _I.alpha_composite(c.convert('RGBA'), _I.new('RGBA', c.size, (255,255,255,0))).convert('RGB')
t = c.crop((0,0,W,120)); b = c.crop((0,235,W,c.height)); o = _I.new('RGB',(W,t.height+b.height),'white'); o.paste(t,(0,0)); o.paste(b,(0,120)); o.save('../SAGIP_Top_View.png'); print(o.size)
