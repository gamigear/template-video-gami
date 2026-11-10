"""Tạo 14 video giữ chỗ (CLIP 01..14) 1920x1080, 8 giây, để dựng thử template.

Chạy: .venv/bin/python travel_cinematic/make_placeholders.py [thư_mục_ra]
"""
import colorsys
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, N, SECONDS = 1920, 1080, 14, 8
FONT = "/System/Library/Fonts/Supplemental/Futura.ttc"


def make_frame(i: int, path: str) -> None:
    # Gradient trời–biển với tông màu đổi theo từng clip để dễ phân biệt khi xem preview
    top = colorsys.hsv_to_rgb((0.55 + i * 0.037) % 1, 0.55, 0.95)
    bottom = colorsys.hsv_to_rgb((0.08 + i * 0.05) % 1, 0.75, 0.55)
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(255 * (a * (1 - t) + b * t)) for a, b in zip(top, bottom))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 220)
    small = ImageFont.truetype(FONT, 56)
    label = f"CLIP {i + 1:02d}"
    d.text((W / 2, H / 2), label, font=big, fill="white", anchor="mm")
    d.text((W / 2, H / 2 + 170), "thay bằng video của bạn", font=small, fill=(255, 255, 255), anchor="mm")
    # Lưới dọc 7 cột để kiểm tra hiệu ứng dải dọc ở intro
    for k in range(1, 7):
        x = k * W // 7
        d.line([(x, 0), (x, 40)], fill="white", width=4)
    img.save(path)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "placeholders")
    os.makedirs(out, exist_ok=True)
    for i in range(N):
        png = os.path.join(out, f"clip_{i + 1:02d}.png")
        mp4 = os.path.join(out, f"clip_{i + 1:02d}.mp4")
        make_frame(i, png)
        # Zoom chậm để clip giữ chỗ là video thật (có chuyển động)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-t", str(SECONDS),
            "-vf", f"scale=2304:-2,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", mp4,
        ], check=True)
        os.remove(png)
        print("ok", mp4)


if __name__ == "__main__":
    main()
