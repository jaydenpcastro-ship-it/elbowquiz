"""Elbow Muscle Review: crop the renders to 800x600 JPEG with a view chip (top-left).
usage: python -P post.py <quiz img dir>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "final")
os.makedirs(DEST, exist_ok=True)
FONT_B = r"C:\Windows\Fonts\seguisb.ttf"
SHOTS = {
    "brachialis": "Right arm · anterolateral view · shoulder ← → hand",
    "biceps": "Right arm · anterior view · shoulder ← → hand",
    "br": "Right forearm · anterolateral view · elbow ← → hand",
    "anconeus": "Right elbow · posterolateral view · arm ← → forearm",
    "pq": "Right forearm · anterior view · elbow ← → hand",
    "supinator": "Right elbow · lateral view · arm ← → forearm",
    "pt": "Right forearm · anterior view · elbow ← → hand",
    "triceps_long": "Right arm · posterior view · shoulder ← → elbow",
}
for name, text in SHOTS.items():
    im = Image.open(os.path.join(HERE, "out", name + ".png")).convert("RGBA").resize((800, 600), Image.LANCZOS)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    f = ImageFont.truetype(FONT_B, 19)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([12, 12, 12 + tw + 18, 12 + 34], radius=9, fill=(14, 18, 32, 220))
    d.text((21, 16), text, font=f, fill=(205, 214, 236, 255))
    im.alpha_composite(ov)
    im.convert("RGB").save(os.path.join(DEST, name + ".jpg"), quality=88)
    print("wrote", name)
