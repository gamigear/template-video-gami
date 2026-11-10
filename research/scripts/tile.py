"""Ghép khung hình preview (pv/NNNN.png) thành ảnh lưới có nhãn thời gian.
python tile.py <dir> <start_frame> <end_frame> <step> <out> [cols]"""
import sys, os
from PIL import Image, ImageDraw
d, a, b, step, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
FPS = 29.961
idx = list(range(a, b + 1, step))
w, h = 320, 180
rows = (len(idx) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (40, 40, 40))
dr = ImageDraw.Draw(sheet)
for k, i in enumerate(idx):
    p = os.path.join(d, f"{i + 1:04d}.png")
    if not os.path.exists(p):
        break
    im = Image.open(p).convert("RGB").resize((w - 2, h - 2))
    x, y = (k % cols) * w, (k // cols) * h
    sheet.paste(im, (x, y))
    dr.rectangle([x, y, x + 92, y + 16], fill=(0, 0, 0))
    dr.text((x + 3, y + 2), f"f{i} {i / FPS:.2f}s", fill=(255, 255, 0))
sheet.save(out, quality=88)
