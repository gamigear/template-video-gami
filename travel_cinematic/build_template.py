"""Dựng draft CapCut "Travel Cinematic" (16:9, 22.5s, 14 clip) theo mẫu reel của Srm Template.

Chạy (đóng CapCut trước):
    .venv/bin/python travel_cinematic/build_template.py                       # dùng clip giữ chỗ
    .venv/bin/python travel_cinematic/build_template.py --clips a.mp4 b.mp4 ... (14 file) \
        --name "Da Nang Trip" --location "DA NANG" --music nhac.mp3

Bố cục (giây, ở 120 BPM; có --music thì tự giãn theo BPM bài nhạc):
    0.0–6.1   Intro nền đen: mỗi phách hiện 1 dải dọc (8 dải, clip 8 + 1–7) kèm chớp trắng, chữ LOCATION,
              viền đen khép từ trên/dưới (闭幕)
    6.6–8.25  Chớp trắng → clip 8 + tiêu đề "Moments / from the Journey"
    8.25–8.6  Lướt nhanh 5 clip (9–13), mỗi clip 2 khung hình
    8.6–20.6  Montage 12 cảnh × 2 phách (clip 1–7, 9–13), zoom nhẹ
    20.6–21.1 Nhấp nháy xen kẽ clip 13/14
    21.1–22.8 Clip 14 + "thank you for everything", mờ dần về đen
"""
import argparse
import copy
import glob
import json
import os
import shutil
import time
import uuid

import numpy as np
import pycapcut as cc

import beats
from draft_check import check_draft
from pycapcut import (ClipSettings, FilterType, FontType, KeyframeProperty, MaskType, TextIntro,
                      TextOutro, TextShadow, TextStyle, TrackType, VideoMaterial, VideoSceneEffectType)

SEC = 1_000_000
FRAME = SEC / 30
W, H = 1920, 1080
DRAFT_ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
MEDIA_ROOT = os.path.expanduser("~/Movies/CapCut/Template Media")
HERE = os.path.dirname(os.path.abspath(__file__))

# Mốc thời gian (giây, ở 120 BPM = 0.5 s/phách), lượng tử hoá theo lưới phách lấy mốc montage 8.6 s
N_STRIPS = 8
STRIP_STARTS = [0.6 + 0.5 * k for k in range(N_STRIPS)]  # mỗi phách hiện thêm 1 dải (0.6 … 4.1)
STRIP_CLIPS = [7, 0, 1, 2, 3, 4, 5, 6]                    # dải đầu là cảnh cầu cảng như mẫu
LOCATION_AT = 4.6                                         # chữ LOCATION
CLOSE_AT = 5.1                                            # viền đen khép từ trên/dưới
CLOSE_END = 6.1                                           # khép kín → màn đen
INTRO_END = 6.6                                           # chớp trắng → cảnh tiêu đề
TITLE_AT = 7.1                                            # chữ tiêu đề
TITLE_END = 8.25
FLASH_END = 8.6
MONTAGE_CUTS = [8.6 + k for k in range(13)]               # 12 cảnh × 2 phách
FLICKER_END = 21.1                                        # nhấp nháy 1 phách
ENDING_TEXT_AT = 21.6
TOTAL = 22.83
WHITE = (1.0, 1.0, 1.0)
LOCATION_RED = (0.80, 0.10, 0.13)   # đo từ khung hình mẫu: (205, 25, 30), độ đục ~0.72
SCRIPT_GOLD = (0.86, 0.88, 0.55)    # chữ script vàng chanh nhạt ở phụ đề
BASE_BPM = 120.0   # video gốc cắt 2 phách/cảnh ở ~120 BPM
TEMPO_SCALE = 1.0  # = BASE_BPM / bpm bài nhạc, đặt trong main()


def us(sec: float) -> int:
    return int(round(sec * SEC))


def tl(sec: float) -> int:
    """Mốc trên timeline: thời gian gốc (nhạc 120 BPM) giãn theo tempo bài nhạc thực tế."""
    return us(sec * TEMPO_SCALE)


def frames(n: int) -> int:
    return int(round(n * FRAME))


class RichText(cc.TextSegment):
    """Text nhiều kiểu trong một dòng (mỗi đoạn một font/màu/cỡ) — CapCut lưu thành nhiều `styles` theo `range`.

    spans: list (chữ, FontType, cỡ, màu, đậm).
    """

    def __init__(self, spans, timerange, **kw):
        super().__init__("".join(sp[0] for sp in spans), timerange, font=spans[0][1], **kw)
        self.spans = spans

    def export_material(self):
        ret = super().export_material()
        content = json.loads(ret["content"])
        base, styles, pos = content["styles"][0], [], 0
        for text, font, size, color, bold in self.spans:
            st = copy.deepcopy(base)
            st.update(range=[pos, pos + len(text)], size=size, bold=bold,
                      font={"id": font.value.resource_id, "path": "D:"})
            st["fill"]["content"]["solid"]["color"] = list(color)
            styles.append(st)
            pos += len(text)
        content["styles"] = styles
        ret["content"] = json.dumps(content, ensure_ascii=False)
        return ret


def script_initials(text, size=9, script_size=13):
    """Chữ cái đầu mỗi từ dùng Pinyon Script vàng chanh, phần còn lại Gloock trắng."""
    spans = []
    for i, word in enumerate(text.split(" ")):
        if i:
            spans.append((" ", FontType.Gloock_Regular, size, WHITE, False))
        if word:
            spans.append((word[0].upper() if i == 0 else word[0], FontType.Pinyon_Script, script_size, SCRIPT_GOLD,
                          False))
            if word[1:]:
                spans.append((word[1:], FontType.Gloock_Regular, size, WHITE, False))
    return spans


class Builder:
    def __init__(self, clips, name):
        self.mats = [VideoMaterial(p, material_name=f"clip_{i + 1:02d}") for i, p in enumerate(clips)]
        self.script = cc.ScriptFile(W, H, 30, maintrack_adsorb=False)
        self.name = name

    # --- tiện ích -----------------------------------------------------------
    def cover_scale(self, mat):
        """Hệ số scale để clip phủ kín khung 16:9 (CapCut mặc định 'fit')."""
        fit = min(W / mat.width, H / mat.height)
        return max(W / (mat.width * fit), H / (mat.height * fit))

    def segment(self, idx, start, dur, *, src_frac=0.0, zoom=None, clip=None):
        """Tạo VideoSegment cho clip `idx` (0-based). Clip ngắn hơn cần thiết sẽ được làm chậm."""
        mat = self.mats[idx]
        scale = self.cover_scale(mat)
        target = cc.Timerange(start, dur)
        if mat.duration >= dur:
            src_start = int((mat.duration - dur) * src_frac)
            seg = cc.VideoSegment(mat, target, source_timerange=cc.Timerange(src_start, dur), volume=0.0,
                                  clip_settings=clip or ClipSettings(scale_x=scale, scale_y=scale))
        else:
            seg = cc.VideoSegment(mat, target, source_timerange=cc.Timerange(0, mat.duration), volume=0.0,
                                  clip_settings=clip or ClipSettings(scale_x=scale, scale_y=scale))
        if zoom:
            seg.add_keyframe(KeyframeProperty.uniform_scale, 0, scale * zoom[0])
            seg.add_keyframe(KeyframeProperty.uniform_scale, dur - 1, scale * zoom[1])
        return seg

    def text(self, track, content, start, dur, *, font=None, size=8, y=0.0, color=(1, 1, 1), bold=False,
             alpha=1.0, spacing=0, intro=TextIntro.渐显, intro_dur=0.5, outro=None, outro_dur=0.4, shadow=False):
        """`content` là chuỗi, hoặc list span (chữ, font, cỡ, màu, đậm) để trộn nhiều kiểu chữ."""
        kw = dict(style=TextStyle(size=size, bold=bold, color=color, alpha=alpha, align=1, letter_spacing=spacing),
                  clip_settings=ClipSettings(transform_y=y),
                  shadow=TextShadow(alpha=0.35, distance=3, diffuse=15) if shadow else None)
        if isinstance(content, str):
            seg = cc.TextSegment(content, cc.Timerange(start, dur), font=font, **kw)
        else:
            seg = RichText(content, cc.Timerange(start, dur), **kw)
        if intro:
            seg.add_animation(intro, us(intro_dur))
        if outro:
            seg.add_animation(outro, us(outro_dur))
        self.script.add_segment(seg, track)

    # --- các phần của template ---------------------------------------------
    def solid(self, path, start, dur, *, mask_strip=None):
        """Đoạn ảnh màu trơn (đen/trắng), tuỳ chọn che còn một dải dọc."""
        seg = cc.VideoSegment(VideoMaterial(path), cc.Timerange(start, dur), volume=0.0)
        if mask_strip is not None:
            self.strip_mask(seg, W, H, mask_strip)
        return seg

    @staticmethod
    def strip_mask(seg, mw, mh, k, scale=1.0):
        """Mask chữ nhật = dải dọc thứ k (rộng W/N_STRIPS), toạ độ tính theo pixel nguồn."""
        px = min(W / mw, H / mh) * scale  # pixel khung hình / pixel nguồn
        strip_w = W / N_STRIPS
        seg.add_mask(MaskType.矩形, center_x=(k - (N_STRIPS - 1) / 2) * strip_w / px, center_y=0,
                     size=1.02 * H / (px * mh), rect_width=strip_w / (px * mw))

    def build(self, location, title, subtitle, tagline, ending, black, white):
        s = self.script
        s.add_track(TrackType.video, "main")
        for k in range(N_STRIPS):
            s.add_track(TrackType.video, f"strip{k + 1}", relative_index=k + 1)
        s.add_track(TrackType.video, "flash", relative_index=N_STRIPS + 1)
        for k in range(1, 5):
            s.add_track(TrackType.text, f"text{k}", relative_index=k)
        s.add_track(TrackType.effect, "fx")
        s.add_track(TrackType.filter, "grade")

        # 1) Intro trên nền đen: mỗi phách hiện thêm 1 dải dọc (1/8 khung), mở đầu bằng chớp trắng 2 khung hình
        s.add_segment(self.solid(black, 0, tl(INTRO_END)), "main")
        for k, (t0, idx) in enumerate(zip(STRIP_STARTS, STRIP_CLIPS)):
            mat = self.mats[idx]
            seg = self.segment(idx, tl(t0), tl(CLOSE_END) - tl(t0), src_frac=0.0)
            self.strip_mask(seg, mat.width, mat.height, k, self.cover_scale(mat))
            s.add_segment(seg, f"strip{k + 1}")
            s.add_segment(self.solid(white, tl(t0), frames(2), mask_strip=k), "flash")

        # Sans hình học rất đậm, đỏ thẫm trong suốt ~75% (nhìn xuyên thấy các dải), rộng ~62% khung
        self.text("text1", location, tl(LOCATION_AT), tl(CLOSE_END) - tl(LOCATION_AT), font=FontType.Poppins_Bold,
                  size=29, bold=True, color=LOCATION_RED, alpha=0.75, intro=TextIntro.渐显, intro_dur=0.15,
                  outro=TextOutro.闭幕, outro_dur=(CLOSE_END - CLOSE_AT) * TEMPO_SCALE)  # chữ khép cùng viền đen
        s.add_effect(VideoSceneEffectType.闭幕, cc.Timerange(tl(CLOSE_AT), tl(CLOSE_END) - tl(CLOSE_AT)), "fx")

        # 2) Màn đen ngắn → chớp trắng → cảnh tiêu đề
        s.add_segment(self.solid(white, tl(INTRO_END), frames(2)), "flash")
        s.add_segment(self.segment(STRIP_CLIPS[0], tl(INTRO_END), tl(TITLE_END) - tl(INTRO_END), src_frac=0.3,
                                   zoom=(1.0, 1.05)), "main")
        t0, d = TITLE_AT, TITLE_END - TITLE_AT
        # "TRAVEL" đậm liền "CINEMATIC" mảnh
        self.text("text1", [("TRAVEL", FontType.Montserrat, 3.2, WHITE, True),
                            ("CINEMATIC", FontType.Montserrat, 3.2, WHITE, False)],
                  tl(t0), tl(d), alpha=0.9, y=0.91, spacing=1)
        # Serif chân nêm, trắng hơi trong
        self.text("text2", title, tl(t0), tl(d), font=FontType.Gloock_Regular, size=26, y=0.09, alpha=0.9,
                  intro=TextIntro.模糊, shadow=True)
        # Serif trắng, chữ cái đầu mỗi từ là script vàng chanh nhạt (giống "From the Journey" của mẫu)
        self.text("text3", script_initials(subtitle), tl(t0 + 0.2), tl(d - 0.2), y=-0.11, shadow=True)
        self.text("text4", tagline, tl(t0 + 0.3), tl(d - 0.3), font=FontType.Montserrat, size=2.5, y=-0.78,
                  alpha=0.9)

        # 3) Lướt nhanh: 5 clip, mỗi clip 2 khung hình
        t = tl(TITLE_END)
        for i, idx in enumerate([8, 9, 10, 11, 12]):
            dur = frames(2) if i < 4 else tl(FLASH_END) - t
            s.add_segment(self.segment(idx, t, dur, src_frac=0.5), "main")
            t += dur

        # 4) Montage 12 cảnh, zoom nhẹ
        order = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12]
        for idx, a, b in zip(order, MONTAGE_CUTS, MONTAGE_CUTS[1:]):
            s.add_segment(self.segment(idx, tl(a), tl(b) - tl(a), src_frac=0.4, zoom=(1.0, 1.05)), "main")

        # 5) Nhấp nháy xen kẽ clip 13/14
        t, i = tl(MONTAGE_CUTS[-1]), 0
        while t < tl(FLICKER_END):
            dur = min(frames(2), tl(FLICKER_END) - t)
            s.add_segment(self.segment(12 if i % 2 == 0 else 13, t, dur, src_frac=0.6), "main")
            t, i = t + dur, i + 1

        # 6) Kết: clip 14 + lời cảm ơn, mờ về đen
        s.add_segment(self.segment(13, tl(FLICKER_END), tl(TOTAL) - tl(FLICKER_END), src_frac=0.6, zoom=(1.0, 1.1)),
                      "main")
        self.text("text1", ending, tl(ENDING_TEXT_AT), tl(TOTAL) - tl(ENDING_TEXT_AT), font=FontType.Montserrat,
                  size=5.5, y=0.04, spacing=6, alpha=0.95, intro=TextIntro.渐显, intro_dur=0.8, outro=TextOutro.渐隐,
                  shadow=True)
        s.add_effect(VideoSceneEffectType.渐隐闭幕, cc.Timerange(tl(TOTAL) - us(0.6), us(0.6)), "fx")

        # Màu điện ảnh teal–cam toàn video
        s.add_filter(FilterType.青橙, cc.Timerange(0, tl(TOTAL)), "grade", intensity=50)

    def add_music(self, path, offset_us=0):
        """Nhạc bắt đầu từ giây `offset_us` của bài (đã chọn sao cho beat khớp với mốc cắt)."""
        audio = cc.AudioMaterial(path, material_name="music")
        dur = min(audio.duration - offset_us, tl(TOTAL))
        seg = cc.AudioSegment(audio, cc.Timerange(0, dur), source_timerange=cc.Timerange(offset_us, dur), volume=1.0)
        seg.add_fade(0, us(0.8))
        self.script.add_track(TrackType.audio, "music")
        self.script.add_segment(seg, "music")


# --- media: CapCut Mac (App Store) chạy sandbox, chỉ đọc được ~/Movies hoặc file người dùng tự chọn ---
def stage_media(paths, folder):
    """Đưa media vào `folder` (trong ~/Movies) bằng hard link, không được thì sao chép."""
    os.makedirs(folder, exist_ok=True)
    out = []
    for p in paths:
        dst = os.path.join(folder, os.path.basename(p))
        if not os.path.exists(dst):
            try:
                os.link(os.path.abspath(p), dst)
            except OSError:
                shutil.copy2(p, dst)
        out.append(dst)
    return out


def solid_images(folder):
    from PIL import Image
    paths = []
    for name, color in (("black.png", (0, 0, 0)), ("white.png", (255, 255, 255))):
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            Image.new("RGB", (W, H), color).save(p)
        paths.append(p)
    return paths


# --- ghi draft theo định dạng CapCut 9.5 macOS -------------------------------
def write_draft(script: cc.ScriptFile, name: str, root: str = DRAFT_ROOT, check: bool = True) -> str:
    folder = os.path.join(root, name)
    if os.path.exists(folder):
        raise SystemExit(f"Đã có draft '{name}'. Đổi --name hoặc xoá thư mục: {folder}")
    os.makedirs(os.path.join(folder, "Timelines"))

    now = int(time.time() * 1_000_000)
    timeline_id = str(uuid.uuid4()).upper()
    script.content["id"] = timeline_id
    script.content["new_version"] = "187.0.0"
    script.content["platform"] = script.content["last_modified_platform"] = {
        "os": "mac", "app_id": 359289, "app_source": "cc", "app_version": "9.5.0"}
    content = script.dumps()

    for p in (os.path.join(folder, "draft_info.json"),
              os.path.join(folder, "Timelines", timeline_id, "draft_info.json")):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    with open(os.path.join(folder, "Timelines", "project.json"), "w", encoding="utf-8") as f:
        json.dump({"config": {"color_space": -1, "hdr_vivid": False, "mixed_track_mode_on": False,
                              "render_index_track_mode_on": False, "use_float_render": False},
                   "create_time": now, "id": str(uuid.uuid4()).upper(), "main_timeline_id": timeline_id,
                   "timelines": [{"create_time": now, "id": timeline_id, "is_marked_delete": False,
                                  "name": "Timeline 01", "update_time": now}],
                   "update_time": now, "version": 0}, f, ensure_ascii=False)

    draft_id = str(uuid.uuid4()).upper()
    with open(cc.assets.get_asset_path("DRAFT_META_TEMPLATE"), encoding="utf-8") as f:
        meta = json.load(f)
    meta.update({"draft_fold_path": folder, "draft_id": draft_id, "draft_name": name, "draft_root_path": root,
                 "tm_draft_create": now, "tm_draft_modified": now, "tm_duration": script.duration})
    with open(os.path.join(folder, "draft_meta_info.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    register(root, folder, name, draft_id, now, script.duration)
    if check:  # chỉ đọc; lỗi của bước kiểm tra không làm hỏng draft đã ghi
        try:
            check_draft(folder)
        except Exception as e:  # noqa: BLE001
            print(f"(bỏ qua bước kiểm tra draft: {e})")
    return folder


def register(root, folder, name, draft_id, now, duration):
    """Thêm draft vào root_meta_info.json để CapCut hiện trong danh sách (có backup)."""
    path = os.path.join(root, "root_meta_info.json")
    shutil.copy(path, path + f".bak_{int(time.time())}")
    with open(path, encoding="utf-8") as f:
        reg = json.load(f)
    entry = copy.deepcopy(reg["all_draft_store"][0]) if reg["all_draft_store"] else {}
    entry.update({
        "draft_cover": "", "draft_fold_path": folder, "draft_id": draft_id,
        "draft_json_file": os.path.join(folder, "draft_info.json"), "draft_name": name,
        "draft_root_path": root, "draft_timeline_materials_size": 0, "draft_cloud_template_id": "",
        "cloud_draft_sync": False, "tm_draft_create": now, "tm_draft_modified": now, "tm_duration": duration,
        "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0, "tm_draft_removed": 0,
    })
    reg["all_draft_store"].insert(0, entry)
    reg["draft_ids"] = int(reg.get("draft_ids", 0)) + 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", nargs="*", help="14 video theo thứ tự (mặc định: clip giữ chỗ)")
    ap.add_argument("--name", default="Travel Cinematic Template")
    ap.add_argument("--location", default="LOCATION")
    ap.add_argument("--title", default="Moments")
    ap.add_argument("--subtitle", default="from the Journey")
    ap.add_argument("--tagline", default="Some journeys end, but the moments we collect along the way stay\n"
                                         "with us forever—reminding us of the places we explored and how alive we felt.")
    ap.add_argument("--ending", default="thank you for everything")
    ap.add_argument("--music", help="file nhạc; tự đo BPM và giãn nhịp cắt cho khớp beat")
    ap.add_argument("--music-at", type=float, default=0.0,
                    help="giây trong bài nhạc sẽ rơi đúng lúc bắt đầu montage (vd: đoạn điệp khúc)")
    ap.add_argument("--out-root", default=DRAFT_ROOT)
    ap.add_argument("--media-root", default=MEDIA_ROOT,
                    help="nơi chép media vào (phải nằm trong ~/Movies vì CapCut Mac chạy sandbox)")
    a = ap.parse_args()

    global TEMPO_SCALE
    offset = 0
    if a.music:
        bpm, phase = beats.detect(a.music)
        while bpm < BASE_BPM / 1.4:  # nhạc chậm: cắt theo nửa phách
            bpm *= 2
        while bpm > BASE_BPM * 1.4:
            bpm /= 2
        TEMPO_SCALE = BASE_BPM / bpm
        period = 60.0 / bpm
        start = MONTAGE_CUTS[0] * TEMPO_SCALE  # mốc montage trên timeline
        # Chọn beat gần `--music-at` nhất mà vẫn còn đủ nhạc phía trước, rồi lùi lại `start` giây
        n = max(round((a.music_at - phase) / period), int(np.ceil((start - phase) / period)))
        offset = us(phase + n * period - start)
        print(f"Nhạc: {bpm:.2f} BPM → giãn nhịp x{TEMPO_SCALE:.4f}, bắt đầu từ giây {offset / SEC:.3f} của bài")

    clips = a.clips or sorted(glob.glob(os.path.join(HERE, "placeholders", "clip_*.mp4")))
    if len(clips) != 14:
        raise SystemExit(f"Cần đúng 14 clip, đang có {len(clips)}")
    if os.path.exists(os.path.join(a.out_root, a.name)):
        raise SystemExit(f"Đã có draft '{a.name}'. Đổi --name hoặc xoá draft cũ trong CapCut.")
    media = os.path.join(a.media_root, a.name)
    clips = stage_media(clips, media)
    black, white = solid_images(media)
    b = Builder(clips, a.name)
    b.build(a.location, a.title, a.subtitle, a.tagline, a.ending, black, white)
    if a.music:
        b.add_music(stage_media([a.music], media)[0], offset)
    folder = write_draft(b.script, a.name, a.out_root)
    print(f"Đã tạo draft: {folder}  ({b.script.duration / SEC:.2f}s)")


if __name__ == "__main__":
    main()
