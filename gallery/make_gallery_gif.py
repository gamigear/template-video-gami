"""Ghép GIF lưới tổng (gallery/gallery.gif): nền tối, mỗi template một thẻ chạy cùng lúc, chấm màu + tên ở dưới.

Đầu vào là thư mục khung hình của từng template:
- HyperFrames: npx hyperframes snapshot --range 0,<độ dài> --frames <n> -o <thư mục>, rồi đổi tên khung theo thứ tự
  thời gian thành f0000.png… (tên gốc frame-100 đứng trước frame-11 khi sắp theo chữ)
- CapCut: python3 gallery/capcut_anim.py "<tên draft>" <thư mục>

Sửa danh sách CARDS bên dưới khi thêm template, rồi chạy:
python3 gallery/make_gallery_gif.py <thư mục tạm> gallery/gallery.gif
"""
import glob
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

FPS = 8
CARD_H = 200
GAP, MARGIN, TOP, LABEL = 20, 28, 78, 56
BG, BORDER = (14, 14, 17), (42, 42, 48)
WHITE, GRAY = (236, 236, 240), (130, 130, 140)
MONO = "/System/Library/Fonts/Menlo.ttc"

# (tên, dòng phụ, màu chấm, mẫu đường dẫn khung, fps của khung, tỉ lệ rộng/cao)
CARDS = [
    ("Logo Nova", "HyperFrames · 9:16", (59, 123, 255), "/tmp/gif_nova_seq/f*.png", 225 / 18.7, 9 / 16),
    ("Spotlight Reveal", "HyperFrames · 9:16", (232, 72, 85), "/tmp/gif_spot_seq/f*.png", 139 / 11.5, 9 / 16),
    ("Travel Cinematic", "CapCut · 16:9", (64, 196, 180), "/tmp/gif_tc/f*.png", 10, 16 / 9),
    ("Welcome Travel Moment", "CapCut · 16:9", (245, 196, 66), "/tmp/gif_wt/f*.png", 10, 16 / 9),
]
TITLE = "template-video-gami"
SUBTITLE = f"{len(CARDS)} templates · HyperFrames + CapCut"


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), m)
    return out


def main():
    tmp, out = sys.argv[1], sys.argv[2]
    os.makedirs(tmp, exist_ok=True)
    cards = []
    for name, sub, dot, pat, fps, ar in CARDS:
        files = sorted(glob.glob(pat))
        cards.append(dict(name=name, sub=sub, dot=dot, files=files, fps=fps, w=round(CARD_H * ar),
                          dur=len(files) / fps))
    total = max(c["dur"] for c in cards)
    f_title = ImageFont.truetype(MONO, 26, index=1)
    f_sub = ImageFont.truetype(MONO, 15)
    f_name = ImageFont.truetype(MONO, 16, index=1)
    for c in cards:  # ô của thẻ rộng ít nhất bằng nhãn, thẻ dọc nằm giữa ô
        lw = 20 + max(f_name.getlength(c["name"]), f_sub.getlength(c["sub"]))
        c["slot"] = max(c["w"], int(lw) + 4)
    width = MARGIN * 2 + sum(c["slot"] for c in cards) + GAP * (len(cards) - 1)
    height = TOP + CARD_H + LABEL + MARGIN // 2

    base = Image.new("RGB", (width, height), BG)
    dr = ImageDraw.Draw(base)
    dr.text((MARGIN, 24), TITLE, font=f_title, fill=WHITE)
    tw = dr.textlength(TITLE, font=f_title)
    dr.text((MARGIN + tw + 16, 33), SUBTITLE, font=f_sub, fill=GRAY)
    x = MARGIN
    for c in cards:
        c["x"] = x + (c["slot"] - c["w"]) // 2
        lx = x
        dr.rounded_rectangle([c["x"] - 1, TOP - 1, c["x"] + c["w"], TOP + CARD_H], 11, outline=BORDER)
        ly = TOP + CARD_H + 14
        dr.ellipse([lx + 2, ly + 4, lx + 12, ly + 14], fill=c["dot"])
        dr.text((lx + 20, ly), c["name"], font=f_name, fill=WHITE)
        dr.text((lx + 20, ly + 21), c["sub"], font=f_sub, fill=GRAY)
        x += c["slot"] + GAP

    n = int(total * FPS)
    cache = {}
    for i in range(n):
        t = i / FPS
        fr = base.copy()
        for c in cards:
            k = int((t % c["dur"]) * c["fps"])  # template ngắn thì lặp lại
            key = c["files"][min(k, len(c["files"]) - 1)]
            if key not in cache:
                im = Image.open(key).convert("RGB").resize((c["w"], CARD_H), Image.LANCZOS)
                cache[key] = rounded(im, 10)
            card = cache[key]
            fr.paste(card, (c["x"], TOP), card)
        fr.save(os.path.join(tmp, f"g{i:04d}.png"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(tmp, "g%04d.png"),
                    "-vf", "split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];"
                           "[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
                    "-loop", "0", out], check=True)
    print(f"{n} khung, {width}×{height} → {out} ({os.path.getsize(out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
