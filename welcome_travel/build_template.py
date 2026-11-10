"""Dựng draft CapCut "Welcome Travel Moment" (16:9, ~25,5 s, 52 cảnh) theo reel mẫu của Vindhx CapCut.

Nguồn: https://www.facebook.com/reel/2054401788599994 (phân tích chi tiết ở README.md).

Chạy (đóng CapCut trước):
    .venv/bin/python welcome_travel/build_template.py                      # dùng 52 clip giữ chỗ
    .venv/bin/python welcome_travel/build_template.py --clips a.mp4 b.mp4 ... \
        --name "Da Nang Trip" --title "DA NANG" --location "VIET NAM" --music nhac.mp3

Bố cục (giây, ở 133,44 BPM; có --music thì tự giãn theo BPM bài nhạc):
    0.00–0.23  màn đen
    0.23–3.17  16 cảnh × 0,18 s; khung mở dần như letterbox (dải ngang → toàn khung);
               chữ WELCOME vàng đổi font liên tục, thu nhỏ 100% → 45%
    3.17–12.8  chớp trắng → "TRAVEL MOMENT / YOUR LOCATION" thu nhỏ 123% → 100% trên cảnh 17–20;
               lóe sáng (light leak) giữa cảnh 18 và 19
    12.7–15.2  khung lồng cảnh 21 bật to từng nấc (40→62→75→84→100%) kèm chớp, rồi thu nhỏ để lộ cảnh 22
    17.4–18.6  trên nền cảnh 23 lần lượt bật khung lồng cảnh 24, 25, 26 (58→70→83%), mỗi lần chớp đen/trắng
    19.0–20.4  cuộn dọc: cảnh 27 → 42 trượt từ trên xuống, ~0,09 s/cảnh
    20.8–25.5  cảnh 43–52, mỗi phách một cảnh, cuối mờ về đen
"""
import argparse
import glob
import importlib.util
import os
import sys

import numpy as np
import pycapcut as cc
from pycapcut import (ClipSettings, FontType, KeyframeProperty as KP, MaskType, TextOutro, TextShadow, TextStyle,
                      TrackType, TransitionType, VideoMaterial, VideoSceneEffectType)

HERE = os.path.dirname(os.path.abspath(__file__))
TRAVEL = os.path.join(HERE, "..", "travel_cinematic")
sys.path.insert(0, TRAVEL)
import beats  # noqa: E402  (travel_cinematic/beats.py)

# Dùng lại phần ghi draft CapCut 9.5 Mac đã kiểm chứng của travel_cinematic (nạp theo đường dẫn vì trùng tên file)
_spec = importlib.util.spec_from_file_location("travel_build", os.path.join(TRAVEL, "build_template.py"))
tc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tc)

SEC = 1_000_000
FRAME = SEC / 30
W, H = 1920, 1080
N_CLIPS = 52
BASE_BPM = 133.44            # đo từ nhạc reel gốc
BEAT = 60 / BASE_BPM         # 0,4496 s
TEMPO_SCALE = 1.0            # = BASE_BPM / BPM bài nhạc thật, đặt trong main()

YELLOW = (0.988, 0.859, 0.345)  # (252, 219, 88) đo từ khung hình mẫu
WHITE = (1.0, 1.0, 1.0)

# --- Mốc thời gian (giây ở 133,44 BPM), đo từng khung hình của reel ---------------------------------------
INTRO_START = 0.234
INTRO_STEP = 0.1836          # 16 cảnh, xen kẽ 5/6 khung hình
INTRO_CLIPS = 16
INTRO_END = INTRO_START + INTRO_CLIPS * INTRO_STEP   # 3.172
# Chiều cao dải hình ở intro (tỉ lệ khung) — viền đen trên/dưới mở dần
BAND = [(0.234, 0.13), (0.30, 0.26), (0.43, 0.38), (0.57, 0.44), (0.77, 0.50), (1.10, 0.54), (1.30, 0.60),
        (1.45, 0.67), (1.57, 0.78), (1.64, 1.0)]
WELCOME_SCALE = [(0.0, 1.0), (1.0, 1.0), (1.8, 0.73), (2.45, 0.60), (3.18, 0.45)]
# (font, cỡ, hệ số co ngang) — cỡ chọn để chiều cao chữ hoa ≈ 28% khung như mẫu
F_BEBAS = (FontType.BebasNeue, 55, 1.0)
F_ANTON = (FontType.Anton, 50, 1.0)
F_AMATIC = (FontType.Amatic_Bold, 57, 1.0)
F_DIDOT = (FontType.Didot_Medium, 54, 0.6)
F_MARKER = (FontType.PermanentMarker_Regular, 40, 1.0)
F_THIN = (FontType.Oswald_ExtraLight, 48, 1.0)
# Mỗi cảnh intro đổi font 2 lần (thứ tự lấy theo mẫu: Bebas là font "nền", xen chữ tay, serif, marker)
WELCOME_FONTS = [F_THIN, F_BEBAS, F_BEBAS, F_AMATIC, F_DIDOT, F_BEBAS, F_MARKER, F_DIDOT,
                 F_BEBAS, F_ANTON, F_DIDOT, F_BEBAS, F_MARKER, F_THIN, F_BEBAS, F_MARKER]

TITLE_AT = 3.204
TITLE_END = 12.80
TITLE_SCALE = [(3.204, 1.23), (4.77, 1.0)]
TITLE_Y = 0.026              # tâm "TRAVEL MOMENT" (đơn vị nửa khung, lên là dương)
LOCATION_Y = -0.253          # tâm "YOUR LOCATION"
TITLE_SQUEEZE = 0.36         # Didot co ngang còn 36% → serif siêu hẹp như mẫu

CUT_18 = 4.773
LEAK_CUT = 7.33              # cảnh 18 → 19, chớp trắng + light leak
CUT_20 = 10.881
PIP_FULL = 13.42             # khung lồng cảnh 21 phủ kín → đổi nền sang cảnh 22
CUT_23 = 16.922
CUT_27 = 18.624
SCROLL_START = 19.047        # cảnh 27 bắt đầu trượt xuống (đo vị trí mép giữa hai cảnh từng khung hình)
SCROLL_STEP = 0.0877         # mép đi 0,39 khung/khung hình → mỗi cảnh cuộn qua mất 0,0877 s
DROP = 20.827                # từ đây mỗi phách một cảnh (beat nhạc khớp ở mốc này)
TOTAL = DROP + 10.5 * BEAT   # 25.55
END_FADE = TOTAL - 0.3

# Khung lồng cảnh 21: (giây, tỉ lệ khung). Giữa các điểm nội suy tuyến tính → nhảy nấc 1–2 khung hình rồi giữ
PIP_A = [(12.72, 0.40), (12.80, 0.62), (12.95, 0.66), (13.00, 0.75), (13.30, 0.76), (13.35, 0.84), (13.42, 1.0),
         (14.42, 1.0), (14.47, 0.86), (14.55, 0.83), (14.72, 0.82), (14.80, 0.66), (15.02, 0.65), (15.09, 0.54),
         (15.15, 0.40)]
PIP_A_END = 15.15
# Chớp trên khung lồng: (giây, số khung hình, màu, độ đục, toàn khung?)
PIP_A_FLASH = [(12.95, 2, "white", 1.0, False), (13.35, 2, "white", 0.6, False), (13.48, 2, "white", 1.0, True),
               (14.42, 2, "white", 0.6, True), (14.69, 2, "white", 1.0, False), (15.02, 2, "white", 0.6, False)]
# Khung lồng trên nền cảnh 23: (cảnh, bắt đầu, kết thúc, tỉ lệ khung)
PIP_B = [(24, 17.36, 17.76, 0.58), (25, 17.76, 18.25, 0.70), (26, 18.25, CUT_27, 0.83)]
PIP_B_FLASH = [(17.36, 2, "black", 0.85), (17.45, 1, "white", 0.7), (17.76, 2, "black", 1.0), (18.25, 2, "white", 1.0)]


def us(sec: float) -> int:
    return int(round(sec * SEC))


def tl(sec: float) -> int:
    """Mốc trên timeline: thời gian gốc (133,44 BPM) giãn theo tempo bài nhạc thực tế."""
    return us(sec * TEMPO_SCALE)


def interp(points, t):
    xs, ys = zip(*points)
    return float(np.interp(t, xs, ys))


def scroll_center(n):
    """Thời điểm cảnh n (27–42) nằm giữa khung trong đoạn cuộn dọc."""
    return SCROLL_START + (n - 27) * SCROLL_STEP


class Builder:
    def __init__(self, clips, black, white, shadow):
        self.mats = [VideoMaterial(p, material_name=f"clip_{i + 1:02d}") for i, p in enumerate(clips)]
        self.solid = {"black": VideoMaterial(black, material_name="black"),
                      "white": VideoMaterial(white, material_name="white")}
        self.shadow = VideoMaterial(shadow, material_name="pip_shadow")
        self.s = cc.ScriptFile(W, H, 30, maintrack_adsorb=False)

    # --- tiện ích -----------------------------------------------------------
    def clip(self, n):
        """Vật liệu cho cảnh n (1–52). Ít clip hơn 52 thì quay vòng."""
        return self.mats[(n - 1) % len(self.mats)]

    @staticmethod
    def cover(mat):
        """Hệ số scale để clip phủ kín khung 16:9 (CapCut mặc định 'fit')."""
        fit = min(W / mat.width, H / mat.height)
        return max(W / (mat.width * fit), H / (mat.height * fit))

    def video(self, n, a, b, *, scale=1.0, y=0.0, src=0.0):
        """VideoSegment cho cảnh n từ a đến b (giây gốc), chưa thêm vào track. Clip ngắn hơn sẽ tự làm chậm."""
        mat = self.clip(n)
        start, dur = tl(a), tl(b) - tl(a)
        sc = self.cover(mat) * scale
        src_tr = (cc.Timerange(int((mat.duration - dur) * src), dur) if mat.duration >= dur
                  else cc.Timerange(0, mat.duration))
        seg = cc.VideoSegment(mat, cc.Timerange(start, dur), source_timerange=src_tr, volume=0.0,
                              clip_settings=ClipSettings(scale_x=sc, scale_y=sc, transform_y=y))
        if abs(mat.width / mat.height - W / H) > 0.02:  # clip khác 16:9: cắt đúng khung để không lấn khi thu nhỏ/trượt
            px = min(W / mat.width, H / mat.height) * self.cover(mat)
            seg.add_mask(MaskType.矩形, size=H / (px * mat.height), rect_width=W / (px * mat.width))
        return seg

    def still(self, name, a, b, *, scale=1.0, y=0.0, alpha=1.0):
        mat = self.solid[name] if name in self.solid else self.shadow
        return cc.VideoSegment(mat, cc.Timerange(tl(a), tl(b) - tl(a)), volume=0.0,
                               clip_settings=ClipSettings(scale_x=scale, scale_y=scale, transform_y=y, alpha=alpha))

    @staticmethod
    def keys(seg, prop, points):
        """Keyframe theo mốc tuyệt đối (giây gốc, giá trị); bỏ điểm nằm ngoài đoạn và điểm trùng thời điểm."""
        start, dur, seen = seg.target_timerange.start, seg.target_timerange.duration, set()
        for t, v in points:
            off = min(max(tl(t) - start, 0), dur - 1)
            if off not in seen:
                seen.add(off)
                seg.add_keyframe(prop, off, v)

    def add(self, seg, track):
        self.s.add_segment(seg, track)
        return seg

    def flash(self, t, n_frames, color, alpha, scale=1.0):
        seg = cc.VideoSegment(self.solid[color], cc.Timerange(tl(t), int(round(n_frames * FRAME))), volume=0.0,
                              clip_settings=ClipSettings(scale_x=scale, scale_y=scale, alpha=alpha))
        self.add(seg, "flash")

    def pip_shadow(self, a, b, points=None, scale=None):
        """Bóng mờ dưới khung lồng: ảnh PNG lớn hơn khung 1,2 lần nên scale = 1,2 × tỉ lệ khung."""
        seg = self.still("shadow", a, b, scale=1.2 * (scale or points[0][1]), alpha=0.55)
        if points:
            self.keys(seg, KP.uniform_scale, [(t, 1.2 * v) for t, v in points])
        self.add(seg, "pip_shadow")

    def text(self, track, content, a, b, *, font, size, color, sx=1.0, scale=1.0, y=0.0, spacing=0, shadow=None,
             scale_keys=None, y_keys=None, outro=None):
        seg = cc.TextSegment(content, cc.Timerange(tl(a), tl(b) - tl(a)), font=font,
                             style=TextStyle(size=size, color=color, align=1, letter_spacing=spacing),
                             clip_settings=ClipSettings(scale_x=sx * scale, scale_y=scale, transform_y=y),
                             shadow=shadow)
        if scale_keys:  # scale_x/scale_y riêng (không dùng uniform_scale) để giữ hệ số co ngang của font
            self.keys(seg, KP.scale_x, [(t, sx * v) for t, v in scale_keys])
            self.keys(seg, KP.scale_y, scale_keys)
        if y_keys:
            self.keys(seg, KP.position_y, y_keys)
        if outro:
            seg.add_animation(outro, us(0.2))
        return self.add(seg, track)

    # --- dựng template -------------------------------------------------------
    def build(self, welcome, title, location):
        s = self.s
        s.add_track(TrackType.video, "main")
        for k, name in enumerate(["pip_shadow", "pip", "scroll_a", "scroll_b", "flash"], start=1):
            s.add_track(TrackType.video, name, relative_index=k)
        s.add_track(TrackType.text, "welcome")
        s.add_track(TrackType.text, "title", relative_index=1)
        s.add_track(TrackType.text, "location", relative_index=2)
        # Viền đen letterbox phải nằm TRÊN chữ (mẫu: chữ WELCOME bị cắt theo dải hình)
        top = TrackType.text.value.render_index + 10
        s.add_track(TrackType.video, "bar_top", absolute_index=top)
        s.add_track(TrackType.video, "bar_bottom", absolute_index=top + 1)
        s.add_track(TrackType.effect, "fx")

        # 1) Intro: màn đen → 16 cảnh × 0,18 s, viền đen trên/dưới mở dần
        self.add(self.still("black", 0, INTRO_START), "main")
        cuts = [INTRO_START + k * INTRO_STEP for k in range(INTRO_CLIPS + 1)]
        for n, (a, b) in enumerate(zip(cuts, cuts[1:]), start=1):
            self.add(self.video(n, a, b, src=0.3), "main")
        band_end = BAND[-1][0]
        for name, sign in (("bar_top", 1), ("bar_bottom", -1)):
            # Ảnh đen toàn khung dời lên/xuống (1 + h) nửa khung → chừa đúng dải cao h ở giữa
            seg = self.still("black", INTRO_START, band_end, y=sign * (1 + BAND[0][1]))
            self.keys(seg, KP.position_y, [(t, sign * (1 + h)) for t, h in BAND])
            self.add(seg, name)

        # WELCOME vàng, mỗi nửa cảnh một font, thu nhỏ dần từ giây 1.0
        glow = TextShadow(alpha=0.45, color=(0, 0, 0), diffuse=25, distance=2)
        halves = [INTRO_START + k * INTRO_STEP / 2 for k in range(2 * INTRO_CLIPS + 1)]
        for j, (a, b) in enumerate(zip(halves, halves[1:])):
            font, size, sx = WELCOME_FONTS[j % len(WELCOME_FONTS)]
            s0, s1 = interp(WELCOME_SCALE, a), interp(WELCOME_SCALE, b)
            self.text("welcome", welcome, a, b, font=font, size=size, color=YELLOW, sx=sx, scale=s0, shadow=glow,
                      scale_keys=[(a, s0), (b, s1)] if abs(s0 - s1) > 1e-4 else None)

        # 2) Tiêu đề: 1 khung đen → chớp trắng → TRAVEL MOMENT / YOUR LOCATION thu nhỏ về 100%
        self.add(self.video(17, INTRO_END, CUT_18, src=0.2), "main")
        self.flash(INTRO_END, 1, "black", 1.0)
        seg = self.still("white", 3.238, 3.371, alpha=0.0)
        self.keys(seg, KP.alpha, [(3.238, 0.0), (3.304, 1.0), (3.371, 0.0)])
        self.add(seg, "flash")
        k0 = TITLE_SCALE[0][1]
        self.text("title", title, TITLE_AT, TITLE_END, font=FontType.Didot_Medium, size=35, color=YELLOW,
                  sx=TITLE_SQUEEZE, scale=k0, y=TITLE_Y * k0, shadow=TextShadow(alpha=0.3, diffuse=20, distance=2),
                  scale_keys=TITLE_SCALE, y_keys=[(t, TITLE_Y * v) for t, v in TITLE_SCALE], outro=TextOutro.渐隐)
        # Hai dòng thu nhỏ quanh tâm khung: dòng phụ vừa nhỏ lại vừa dịch về giữa
        self.text("location", location, TITLE_AT, TITLE_END, font=FontType.CINZEL, size=7, color=WHITE, spacing=4,
                  scale=k0, y=LOCATION_Y * k0, scale_keys=TITLE_SCALE,
                  y_keys=[(t, LOCATION_Y * v) for t, v in TITLE_SCALE], outro=TextOutro.渐隐)

        # Cảnh 18 → 19: chớp trắng (chuyển cảnh miễn phí) + lóe sáng phim
        seg = self.video(18, CUT_18, LEAK_CUT, src=0.2)
        seg.add_transition(TransitionType.闪白, duration=tl(0.27))
        self.add(seg, "main")
        s.add_effect(VideoSceneEffectType.胶片漏光, cc.Timerange(tl(7.05), tl(7.65) - tl(7.05)), "fx")
        self.add(self.video(19, LEAK_CUT, CUT_20, src=0.1), "main")
        self.add(self.video(20, CUT_20, PIP_FULL, src=0.1), "main")

        # 3) Khung lồng cảnh 21 bật to từng nấc trên cảnh 20, phủ kín, rồi thu nhỏ để lộ cảnh 22
        a0 = PIP_A[0][0]
        seg = self.video(21, a0, PIP_A_END, scale=PIP_A[0][1])
        self.keys(seg, KP.uniform_scale, [(t, self.cover(self.clip(21)) * v) for t, v in PIP_A])
        self.add(seg, "pip")
        self.pip_shadow(a0, PIP_A_END, points=PIP_A)
        for t, nf, color, alpha, full in PIP_A_FLASH:
            self.flash(t, nf, color, alpha, 1.0 if full else interp(PIP_A, t))
        self.add(self.video(22, PIP_FULL, CUT_23), "main")

        # 4) Nền cảnh 23, lần lượt bật khung lồng cảnh 24, 25, 26
        self.add(self.video(23, CUT_23, CUT_27), "main")
        for n, a, b, sc in PIP_B:
            self.add(self.video(n, a, b, scale=sc, src=0.2), "pip")
            self.pip_shadow(a, b, scale=sc)
        for t, nf, color, alpha in PIP_B_FLASH:
            self.flash(t, nf, color, alpha, next(sc for _, a, b, sc in PIP_B if a <= t < b))

        # 5) Cuộn dọc 27 → 42: mỗi cảnh trượt từ trên (y=+2) qua giữa (0) xuống dưới (-2), hai track xen kẽ
        c = scroll_center
        seg = self.video(27, CUT_27, c(28))
        self.keys(seg, KP.position_y, [(c(27), 0.0), (c(28), -2.0)])
        self.add(seg, "main")
        for n in range(28, 42):
            seg = self.video(n, c(n - 1), c(n + 1), y=2.0, src=0.3)
            self.keys(seg, KP.position_y, [(c(n - 1), 2.0), (c(n), 0.0), (c(n + 1), -2.0)])
            self.add(seg, "scroll_a" if n % 2 == 0 else "scroll_b")
        # Cảnh 42 nằm sẵn trên track chính (ngoài khung) để track chính liền mạch, trượt vào ở cuối đoạn cuộn
        seg = self.video(42, c(28), DROP, y=2.0)
        self.keys(seg, KP.position_y, [(c(41), 2.0), (c(42), 0.0)])
        self.add(seg, "main")

        # 6) Cảnh 43–52: mỗi phách một cảnh, cảnh cuối dài 1,5 phách, mờ về đen
        beats_ = [DROP + k * BEAT for k in range(10)] + [TOTAL]
        for n, (a, b) in enumerate(zip(beats_, beats_[1:]), start=43):
            self.add(self.video(n, a, b, src=0.3), "main")
        seg = self.still("black", END_FADE, TOTAL, alpha=0.0)
        self.keys(seg, KP.alpha, [(END_FADE, 0.0), (TOTAL, 1.0)])
        self.add(seg, "flash")

    def add_music(self, path, offset_us=0):
        audio = cc.AudioMaterial(path, material_name="music")
        dur = min(audio.duration - offset_us, tl(TOTAL))
        seg = cc.AudioSegment(audio, cc.Timerange(0, dur), source_timerange=cc.Timerange(offset_us, dur), volume=1.0)
        seg.add_fade(0, us(0.5))
        self.s.add_track(TrackType.audio, "music")
        self.s.add_segment(seg, "music")


def shadow_image(folder):
    """PNG bóng mờ: chữ nhật đen 1920x1080 làm mờ, đặt giữa ảnh 2304x1296 trong suốt."""
    from PIL import Image, ImageFilter
    p = os.path.join(folder, "pip_shadow.png")
    if not os.path.exists(p):
        mw, mh = int(W * 1.2), int(H * 1.2)
        a = Image.new("L", (mw, mh), 0)
        a.paste(255, ((mw - W) // 2, (mh - H) // 2, (mw + W) // 2, (mh + H) // 2))
        a = a.filter(ImageFilter.GaussianBlur(40))
        img = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        img.putalpha(a)
        img.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", nargs="*", help=f"tối đa {N_CLIPS} video theo thứ tự (ít hơn thì quay vòng; "
                                               "mặc định: clip giữ chỗ)")
    ap.add_argument("--name", default="Welcome Travel Moment Template")
    ap.add_argument("--welcome", default="WELCOME")
    ap.add_argument("--title", default="TRAVEL MOMENT")
    ap.add_argument("--location", default="YOUR LOCATION")
    ap.add_argument("--music", help="file nhạc; tự đo BPM và giãn nhịp cắt cho khớp beat")
    ap.add_argument("--music-at", type=float, default=0.0,
                    help="giây trong bài nhạc sẽ rơi đúng mốc 'drop' (cảnh 43, bắt đầu cắt theo từng phách)")
    ap.add_argument("--out-root", default=tc.DRAFT_ROOT)
    ap.add_argument("--media-root", default=tc.MEDIA_ROOT,
                    help="nơi chép media vào (phải nằm trong ~/Movies vì CapCut Mac chạy sandbox)")
    a = ap.parse_args()
    missing = [p for p in (a.clips or []) + ([a.music] if a.music else []) if not os.path.isfile(p)]
    if missing:
        raise SystemExit("Không tìm thấy file: " + ", ".join(missing) +
                         f"\n(đường dẫn tính từ thư mục đang đứng: {os.getcwd()})")

    global TEMPO_SCALE
    offset = 0
    if a.music:
        bpm, phase = beats.detect(a.music)
        while bpm < BASE_BPM / 1.4:
            bpm *= 2
        while bpm > BASE_BPM * 1.4:
            bpm /= 2
        TEMPO_SCALE = BASE_BPM / bpm
        period = 60.0 / bpm
        start = DROP * TEMPO_SCALE
        # Beat gần `--music-at` nhất mà vẫn đủ nhạc phía trước, rồi lùi lại `start` giây
        n = max(round((a.music_at - phase) / period), int(np.ceil((start - phase) / period)))
        offset = us(phase + n * period - start)
        print(f"Nhạc: {bpm:.2f} BPM → giãn nhịp x{TEMPO_SCALE:.4f}, bắt đầu từ giây {offset / SEC:.3f} của bài")

    clips = a.clips or sorted(glob.glob(os.path.join(HERE, "placeholders", "clip_*.mp4")))
    if not 1 <= len(clips) <= N_CLIPS:
        raise SystemExit(f"Cần 1–{N_CLIPS} clip, đang có {len(clips)}")
    if len(clips) < N_CLIPS:
        print(f"Có {len(clips)} clip cho {N_CLIPS} cảnh → dùng quay vòng")
    if os.path.exists(os.path.join(a.out_root, a.name)):
        raise SystemExit(f"Đã có draft '{a.name}'. Đổi --name hoặc xoá draft cũ trong CapCut.")
    media = os.path.join(a.media_root, a.name)
    clips = tc.stage_media(clips, media)
    black, white = tc.solid_images(media)
    b = Builder(clips, black, white, shadow_image(media))
    b.build(a.welcome, a.title, a.location)
    if a.music:
        b.add_music(tc.stage_media([a.music], media)[0], offset)
    folder = tc.write_draft(b.s, a.name, a.out_root)
    print(f"Đã tạo draft: {folder}  ({b.s.duration / SEC:.2f}s)")


if __name__ == "__main__":
    main()
