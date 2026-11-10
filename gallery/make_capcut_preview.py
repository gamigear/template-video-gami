"""Dựng ảnh xem trước (dải khung hình) cho một draft CapCut, dùng bộ dựng gần đúng ở research/scripts/preview_draft.py.
Không có mask, filter, hiệu ứng, chuyển cảnh: chỉ thấy bố cục, chữ, scale, độ đục.

python3 gallery/make_capcut_preview.py "<tên draft>" <ảnh ra.jpg> t1 t2 ...
"""
import importlib.util
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("preview_draft", os.path.join(HERE, "..", "research", "scripts", "preview_draft.py"))
pd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pd)

DRAFTS = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")


def main():
    name, out, *ts = sys.argv[1:]
    d = json.load(open(os.path.join(DRAFTS, name, "draft_info.json"), encoding="utf-8"))
    frames = [pd.render(d, int(float(t) * 1e6)) for t in ts]
    w, h, g = 480, 270, 8
    cols = 3
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + g) - g, rows * (h + g) - g), (18, 18, 18))
    for i, im in enumerate(frames):
        sheet.paste(im.resize((w, h), Image.LANCZOS), ((i % cols) * (w + g), (i // cols) * (h + g)))
    sheet.save(out, quality=86)


if __name__ == "__main__":
    main()
