"""Tạo 52 video giữ chỗ (CLIP 01..52) 1920x1080, 4 giây, màu trơn như bản mẫu, để dựng thử template.

Chạy: .venv/bin/python welcome_travel/make_placeholders.py [thư_mục_ra]
"""
import colorsys
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, N, SECONDS = 1920, 1080, 52, 4
FONT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def make_frame(i: int, path: str) -> None:
    # Màu đổi mạnh giữa hai clip liền nhau (bước hue ~0.38) để dễ thấy nhịp cắt khi xem preview
    h = (i * 0.381966) % 1
    top = np.array(colorsys.hsv_to_rgb(h, 0.75, 0.95)) * 255
    bottom = np.array(colorsys.hsv_to_rgb(h, 0.85, 0.70)) * 255
    t = np.linspace(0, 1, H)[:, None, None]
    img = Image.fromarray(np.broadcast_to(top * (1 - t) + bottom * t, (H, W, 3)).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2), f"CLIP {i + 1:02d}", font=ImageFont.truetype(FONT, 150, index=1), fill="white",
           anchor="mm")
    # Khung viền mảnh để thấy rõ cảnh nằm ở đâu khi thu nhỏ (khung lồng) hoặc trượt dọc
    d.rectangle([12, 12, W - 13, H - 13], outline="white", width=6)
    img.save(path)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "placeholders")
    os.makedirs(out, exist_ok=True)
    for i in range(N):
        png = os.path.join(out, f"clip_{i + 1:02d}.png")
        mp4 = os.path.join(out, f"clip_{i + 1:02d}.mp4")
        if os.path.exists(mp4):
            continue
        make_frame(i, png)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-t", str(SECONDS),
                        "-vf", "fps=30", "-c:v", "libx264", "-pix_fmt", "yuv420p", mp4], check=True)
        os.remove(png)
    print(f"ok: {N} clip trong {out}")


if __name__ == "__main__":
    main()
