"""Dựng chuỗi khung hình động (gần đúng) từ draft CapCut để làm GIF xem trước.

So với research/scripts/preview_draft.py (chỉ lấy khung đầu mỗi clip), bản này có:
- clip chạy theo thời gian (source_timerange + speed);
- mask chữ nhật (dải dọc của Travel Cinematic);
- animation vào/ra của clip và chữ, tính như fade;
- vài hiệu ứng tính gần đúng: 闭幕 (khép màn), 渐隐闭幕 (mờ về đen), 胶片漏光 (loé sáng phim),
  chuyển cảnh 闪白 (loé trắng), filter 青橙 (teal–cam).

Font CapCut không có trên máy được thay bằng font sẵn có, nên chữ chỉ đúng vị trí và cỡ, không đúng mặt chữ.

python3 gallery/capcut_anim.py "<tên draft>" <thư mục khung ra> [--fps 10] [--width 480] [--from 0] [--to <hết>]
"""
import argparse
import hashlib
import json
import os
import subprocess
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DRAFTS = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
CACHE = os.path.expanduser("~/Movies/CapCut/User Data/Cache/effect")
KNOWN_FONTS = {
    "7194703888736326146": f"{CACHE}/11612853/d222fc4f8018cbdecde64a81a3944e3f/Didot-Medium06.ttf",
    "7044872180428968449": f"{CACHE}/1271323/39f57acca697657a16fe9d5e83d39f52/CinzelDecorative-Bold.ttf",
}
SUBSTITUTES = [  # font thay thế cho id lạ, chọn theo hash id để mỗi font CapCut ra một mặt chữ khác nhau
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/Supplemental/Rockwell.ttc",
    "/System/Library/Fonts/Supplemental/Copperplate.ttc",
    "/System/Library/Fonts/Supplemental/Bodoni 72.ttc",
]


def font_path(fid):
    if fid in KNOWN_FONTS and os.path.exists(KNOWN_FONTS[fid]):
        return KNOWN_FONTS[fid]
    ok = [p for p in SUBSTITUTES if os.path.exists(p)]
    return ok[int(hashlib.md5(fid.encode()).hexdigest(), 16) % len(ok)]


def kf(seg, prop, default):
    for k in seg.get("common_keyframes", []):
        if k["property_type"] == prop:
            pts = sorted((x["time_offset"], x["values"][0]) for x in k["keyframe_list"])
            return lambda off: float(np.interp(off, [p[0] for p in pts], [p[1] for p in pts]))
    return lambda off: default


class Frames:
    """Lấy khung của file video tại giây t (bộ đệm theo khung 1/30 s)."""

    def __init__(self, width):
        self.width, self.cache = width, {}

    def get(self, path, t):
        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            key = (path, 0)
        else:
            key = (path, round(t * 30))
        if key not in self.cache:
            if key[1] == 0 and path.lower().endswith((".png", ".jpg", ".jpeg")):
                im = Image.open(path).convert("RGBA")
                im = im.resize((self.width, max(1, round(im.height * self.width / im.width))), Image.LANCZOS)
            else:
                raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{key[1] / 30:.3f}", "-i", path,
                                      "-frames:v", "1", "-vf", f"scale={self.width}:-2", "-f", "image2pipe",
                                      "-vcodec", "png", "-"], capture_output=True).stdout
                if not raw:  # quá cuối file: lấy khung cuối
                    raw = subprocess.run(["ffmpeg", "-v", "error", "-sseof", "-0.1", "-i", path, "-frames:v", "1",
                                          "-vf", f"scale={self.width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                                         capture_output=True, check=True).stdout
                im = Image.open(BytesIO(raw)).convert("RGBA")
            self.cache[key] = im
        return self.cache[key]


def rect_mask(size, cfg):
    w, h = size
    m = Image.new("L", size, 0)
    cx, cy = (cfg["centerX"] + 1) / 2 * w, (1 - cfg["centerY"]) / 2 * h
    mw, mh = cfg["width"] * w, cfg["height"] * h
    ImageDraw.Draw(m).rectangle([cx - mw / 2, cy - mh / 2, cx + mw / 2, cy + mh / 2], fill=255)
    if cfg.get("invert"):
        m = Image.eval(m, lambda v: 255 - v)
    return m


def teal_orange(rgb, k=0.18):
    a = np.asarray(rgb).astype(np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    d = (lum - 0.45)[..., None] * k * np.array([1.0, 0.15, -1.0], np.float32)
    a = np.clip(a + d, 0, 1)
    gray = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = np.clip(gray[..., None] + (a - gray[..., None]) * 1.12, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


class Renderer:
    def __init__(self, d, width):
        self.d = d
        cw, ch = d["canvas_config"]["width"], d["canvas_config"]["height"]
        self.W, self.H = width, round(width * ch / cw)
        self.px_per_size = 8 * self.H / 1080  # ≈ 8 px mỗi đơn vị cỡ chữ trên khung cao 1080 (đã hiệu chỉnh)
        m = d["materials"]
        self.videos = {x["id"]: x for x in m["videos"]}
        self.texts = {x["id"]: x for x in m["texts"]}
        self.masks = {x["id"]: x for x in m.get("masks", [])}
        self.anims = {x["id"]: x for x in m.get("material_animations", [])}
        self.trans = {x["id"]: x for x in m.get("transitions", [])}
        fx = {x["id"]: x for k in ("video_effects", "effects") for x in m.get(k, [])}
        self.frames = Frames(width)
        self.tracks = sorted((tr for tr in d["tracks"] if tr["segments"]),
                             key=lambda tr: tr["segments"][0]["render_index"])
        self.effects, self.flashes = [], []
        for tr in d["tracks"]:
            for s in tr["segments"]:
                tt = s["target_timerange"]
                if tr["type"] in ("effect", "filter") and s["material_id"] in fx:
                    self.effects.append((fx[s["material_id"]].get("name"), tt["start"], tt["duration"]))
                for r in s.get("extra_material_refs", []):
                    if r in self.trans:  # chuyển cảnh nằm ở cuối clip, phủ đều hai bên điểm cắt
                        dur = self.trans[r]["duration"]
                        self.flashes.append((tt["start"] + tt["duration"], dur))

    def anim_alpha(self, seg, off):
        a, dur = 1.0, seg["target_timerange"]["duration"]
        for r in seg.get("extra_material_refs", []):
            for an in self.anims.get(r, {}).get("animations", []):
                d = max(1, an["duration"])
                if an["type"] == "in":
                    a *= min(1.0, off / d)
                elif an["type"] == "out":
                    a *= min(1.0, max(0.0, (dur - off) / d))
        return a

    def layer_text(self, seg):
        content = json.loads(self.texts[seg["material_id"]]["content"])
        st = content["styles"][0]
        font = ImageFont.truetype(font_path(st["font"]["id"]), max(4, int(st["size"] * self.px_per_size)))
        color = tuple(int(255 * v) for v in st["fill"]["content"]["solid"]["color"])
        bb = font.getbbox(content["text"])
        base = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (0, 0, 0, 0))
        ImageDraw.Draw(base).text((2 - bb[0], 2 - bb[1]), content["text"], font=font, fill=color + (255,))
        return base

    def render(self, t_us):
        W, H = self.W, self.H
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        for tr in self.tracks:
            if tr["type"] not in ("video", "text"):
                continue
            for seg in tr["segments"]:
                tt = seg["target_timerange"]
                if not tt["start"] <= t_us < tt["start"] + tt["duration"]:
                    continue
                off = t_us - tt["start"]
                c = seg["clip"]
                sx = kf(seg, "KFTypeScaleX", c["scale"]["x"])(off)
                uniform = seg.get("uniform_scale", {}).get("on", True)
                sy = sx if uniform and tr["type"] == "video" else kf(seg, "KFTypeScaleY", c["scale"]["y"])(off)
                tx = kf(seg, "KFTypePositionX", c["transform"]["x"])(off)
                ty = kf(seg, "KFTypePositionY", c["transform"]["y"])(off)
                alpha = kf(seg, "KFTypeAlpha", c["alpha"])(off) * self.anim_alpha(seg, off)
                if alpha <= 0.01:
                    continue
                if tr["type"] == "video":
                    m = self.videos[seg["material_id"]]
                    src_t = (seg["source_timerange"]["start"] + off * seg.get("speed", 1.0)) / 1e6
                    src = self.frames.get(m["path"], src_t)
                    fit = min(W / src.width, H / src.height)
                    w, h = max(1, int(src.width * fit * sx)), max(1, int(src.height * fit * sy))
                    layer = src.resize((w, h))
                    for r in seg.get("extra_material_refs", []):
                        if r in self.masks:
                            mk = rect_mask((w, h), self.masks[r]["config"])
                            layer.putalpha(Image.fromarray(np.minimum(np.asarray(layer.getchannel("A")),
                                                                      np.asarray(mk))))
                else:
                    base = self.layer_text(seg)
                    w, h = max(1, int(base.width * sx)), max(1, int(base.height * sy))
                    layer = base.resize((w, h))
                if alpha < 1:
                    layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
                cx, cy = W / 2 + tx * W / 2, H / 2 - ty * H / 2
                x0, y0 = int(cx - w / 2), int(cy - h / 2)
                if -w < x0 < W and -h < y0 < H:
                    canvas.alpha_composite(layer, (x0, y0))
        img = canvas.convert("RGB")
        for name, start, dur in self.effects:
            if not start <= t_us < start + dur:
                continue
            p = (t_us - start) / dur
            if name == "青橙":
                img = teal_orange(img)
            elif name == "闭幕":  # hai thanh đen khép từ trên và dưới
                bar = int(H / 2 * min(1.0, p * 1.15))
                dr = ImageDraw.Draw(img)
                dr.rectangle([0, 0, W, bar], fill=0)
                dr.rectangle([0, H - bar, W, H], fill=0)
            elif name == "渐隐闭幕":
                img = Image.blend(img, Image.new("RGB", img.size, 0), min(1.0, p))
            elif name == "胶片漏光":
                k = np.sin(np.pi * p)
                leak = Image.new("RGB", img.size, (255, 140, 40))
                grad = Image.linear_gradient("L").rotate(90).resize(img.size).point(lambda v: int(v * 0.75 * k))
                img = Image.composite(leak, img, grad.filter(ImageFilter.GaussianBlur(W / 20)))
        for at, dur in self.flashes:
            if abs(t_us - at) < dur / 2:
                k = 1 - abs(t_us - at) / (dur / 2)
                img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), 0.9 * k)
        return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--from", dest="t0", type=float, default=0)
    ap.add_argument("--to", dest="t1", type=float)
    a = ap.parse_args()
    d = json.load(open(os.path.join(DRAFTS, a.name, "draft_info.json"), encoding="utf-8"))
    r = Renderer(d, a.width)
    t1 = a.t1 if a.t1 is not None else d["duration"] / 1e6
    os.makedirs(a.out, exist_ok=True)
    n = int((t1 - a.t0) * a.fps)
    for i in range(n):
        r.render(int((a.t0 + i / a.fps) * 1e6)).save(os.path.join(a.out, f"f{i:04d}.png"))
    print(f"{n} khung → {a.out}")


if __name__ == "__main__":
    main()
