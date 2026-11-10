"""Dựng thử khung hình từ draft_info.json (gần đúng) để so với reel mẫu — không thay CapCut, chỉ kiểm tra
thời điểm, scale, vị trí, keyframe, độ đục. Chữ vẽ bằng font thay thế, video lấy khung đầu của file.

python -I preview_draft.py <thư mục draft> <reel.mp4> <ảnh ra> t1 t2 ...
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540              # dựng ở nửa độ phân giải
PX_PER_SIZE = 8 * H / 1080   # ≈ 8 px mỗi đơn vị cỡ chữ trên khung 1080p (đã hiệu chỉnh trước đây)
CACHE = os.path.expanduser("~/Movies/CapCut/User Data/Cache/effect")
FONTS = {  # font id CapCut → font thay thế trên máy (chỉ để ước lượng kích thước)
    "7194703888736326146": f"{CACHE}/11612853/d222fc4f8018cbdecde64a81a3944e3f/Didot-Medium06.ttf",
    "7044872180428968449": f"{CACHE}/1271323/39f57acca697657a16fe9d5e83d39f52/CinzelDecorative-Bold.ttf",
}
FALLBACK = "/System/Library/Fonts/Supplemental/Impact.ttf"


def kf_value(seg, prop, default):
    for k in seg.get("common_keyframes", []):
        if k["property_type"] == prop:
            pts = sorted((x["time_offset"], x["values"][0]) for x in k["keyframe_list"])
            return lambda off: float(np.interp(off, [p[0] for p in pts], [p[1] for p in pts]))
    return lambda off: default


def frame_of(path, cache={}):
    if path not in cache:
        if path.lower().endswith((".png", ".jpg")):
            im = Image.open(path).convert("RGBA")
        else:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-frames:v", "1", "-f", "image2pipe",
                                  "-vcodec", "png", "-"], capture_output=True, check=True).stdout
            from io import BytesIO
            im = Image.open(BytesIO(raw)).convert("RGBA")
        cache[path] = im
    return cache[path]


def render(d, t_us):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    mats = {m["id"]: m for m in d["materials"]["videos"]}
    texts = {m["id"]: m for m in d["materials"]["texts"]}
    tracks = sorted(d["tracks"], key=lambda tr: tr["segments"][0]["render_index"] if tr["segments"] else 0)
    for tr in tracks:
        if tr["type"] not in ("video", "text"):
            continue
        for seg in tr["segments"]:
            tt = seg["target_timerange"]
            if not tt["start"] <= t_us < tt["start"] + tt["duration"]:
                continue
            off = t_us - tt["start"]
            c = seg["clip"]
            sx = kf_value(seg, "KFTypeScaleX", c["scale"]["x"])(off)
            uniform = seg.get("uniform_scale", {}).get("on", True)
            sy = sx if uniform and tr["type"] == "video" else kf_value(seg, "KFTypeScaleY", c["scale"]["y"])(off)
            tx = kf_value(seg, "KFTypePositionX", c["transform"]["x"])(off)
            ty = kf_value(seg, "KFTypePositionY", c["transform"]["y"])(off)
            alpha = kf_value(seg, "KFTypeAlpha", c["alpha"])(off)
            if tr["type"] == "video":
                m = mats[seg["material_id"]]
                src = frame_of(m["path"])
                fit = min(W / src.width, H / src.height)
                w, h = max(1, int(src.width * fit * sx)), max(1, int(src.height * fit * sy))
                layer = src.resize((w, h))
            else:
                content = json.loads(texts[seg["material_id"]]["content"])
                st = content["styles"][0]
                font = ImageFont.truetype(FONTS.get(st["font"]["id"], FALLBACK), max(4, int(st["size"] * PX_PER_SIZE)))
                color = tuple(int(255 * v) for v in st["fill"]["content"]["solid"]["color"])
                bb = font.getbbox(content["text"])
                base = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
                ImageDraw.Draw(base).text((2 - bb[0], 2 - bb[1]), content["text"], font=font, fill=color + (255,))
                w, h = max(1, int(base.width * sx)), max(1, int(base.height * sy))
                layer = base.resize((w, h))
            if alpha < 1:
                a = layer.getchannel("A").point(lambda v: int(v * alpha))
                layer.putalpha(a)
            cx, cy = W / 2 + tx * W / 2, H / 2 - ty * H / 2
            canvas.alpha_composite(layer, (int(cx - w / 2), int(cy - h / 2))) if (
                    -w < cx - w / 2 < W and -h < cy - h / 2 < H) else None
    return canvas.convert("RGB")


def reel_frame(reel, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", reel, "-frames:v", "1",
                          "-vf", f"crop=1080:608:0:178,scale={W}:{H}", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB")


def main():
    folder, reel, out, *ts = sys.argv[1:]
    d = json.load(open(os.path.join(folder, "draft_info.json"), encoding="utf-8"))
    ts = [float(x) for x in ts]
    tw, th = W // 2, H // 2
    sheet = Image.new("RGB", (tw * 2 + 6, (th + 4) * len(ts)), (60, 60, 60))
    dr = ImageDraw.Draw(sheet)
    for i, t in enumerate(ts):
        y = i * (th + 4)
        sheet.paste(reel_frame(reel, t).resize((tw, th)), (0, y))
        sheet.paste(render(d, int(t * 1e6)).resize((tw, th)), (tw + 6, y))
        dr.rectangle([0, y, 150, y + 18], fill=(0, 0, 0))
        dr.text((4, y + 3), f"{t:.2f}s  reel | draft", fill=(255, 255, 0))
    sheet.save(out, quality=88)


if __name__ == "__main__":
    main()
