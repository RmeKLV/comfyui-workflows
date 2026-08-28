"""Face-centred split of the 2048x1024 two-shots into 1024x1024 PFPs.

Runs face_yolov8m over each wide render, sorts the boxes left-to-right and takes a
full-height square window centred on each face (clamped to the canvas). Do NOT cut the
image 50/50 — that pushes each face toward the outer edge of a circular avatar mask.
Also writes a contact sheet of circular previews, which is what the platform shows and
the fastest way to judge a candidate.

    python scripts/split_pfp.py
"""
import os, glob, json
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

ROOT = "ComfyUI/output/matching_v4"
WIDE = os.path.join(ROOT, "wide")
PFP = os.path.join(ROOT, "pfp")
os.makedirs(PFP, exist_ok=True)

det = YOLO("ComfyUI/models/ultralytics/bbox/face_yolov8m.pt")


def faces(img_path):
    r = det(img_path, conf=0.35, verbose=False)[0]
    b = [tuple(map(float, x)) for x in r.boxes.xyxy.tolist()]
    b.sort(key=lambda t: t[0])
    return b


def crop_square(im, cx):
    H = im.height
    left = max(0, min(im.width - H, int(cx - H / 2)))
    return im.crop((left, 0, left + H, H)).resize((1024, 1024), Image.LANCZOS)


rows = []
for p in sorted(glob.glob(os.path.join(WIDE, "*.png"))):
    name = os.path.basename(p).replace("_00001_", "").replace("_00002_", "").replace(".png", "")
    im = Image.open(p).convert("RGB")
    fb = faces(p)
    if len(fb) != 2:
        print("SKIP %-18s %d faces detected" % (name, len(fb)))
        rows.append((name, im.resize((1024, 512), Image.LANCZOS), None, len(fb)))
        continue
    crops = []
    for i, (x1, y1, x2, y2) in enumerate(fb):
        c = crop_square(im, (x1 + x2) / 2)
        out = os.path.join(PFP, "%s_%s.png" % (name, "L" if i == 0 else "R"))
        c.save(out)
        crops.append(c)
    rows.append((name, crops[0], crops[1], 2))
    print("OK   %-18s 2 faces -> L/R" % name)

# contact sheet: circular previews, 2 per row
T, PAD, LBL = 300, 18, 22
cols = 2
n = len(rows)
sheet_w = cols * (T * 2 + PAD * 3)
sheet_h = ((n + cols - 1) // cols) * (T + LBL + PAD * 2)
sheet = Image.new("RGB", (sheet_w, sheet_h), "#f5f5f5")
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("arial.ttf", 16)
except Exception:
    font = ImageFont.load_default()

mask = Image.new("L", (T, T), 0)
ImageDraw.Draw(mask).ellipse((0, 0, T - 1, T - 1), fill=255)

for i, (name, a, b, nf) in enumerate(rows):
    cx = (i % cols) * (T * 2 + PAD * 3) + PAD
    cy = (i // cols) * (T + LBL + PAD * 2) + PAD
    d.text((cx, cy), "%s  (%d faces)" % (name, nf), fill="#222", font=font)
    y = cy + LBL
    if b is None:
        sheet.paste(a.resize((T * 2, T), Image.LANCZOS), (cx, y))
    else:
        for j, c in enumerate((a, b)):
            t = c.resize((T, T), Image.LANCZOS)
            sheet.paste(t, (cx + j * (T + PAD), y), mask)
out = os.path.join(ROOT, "_contact_sheet_v4.png")
sheet.save(out)
print("sheet ->", out)
