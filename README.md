# Template Video Gami: gallery template

Bộ template video dựng lại từ các reel mẫu: phân tích từng khung hình, rồi dựng lại **bố cục, nhịp cắt, chuyển động và kiểu chữ**.
Không dùng lại video, nhạc hay đồ hoạ của tác giả gốc.

Có hai loại:

- **HyperFrames:** video bằng HTML + GSAP, sửa trong Studio, render ra MP4.
- **CapCut Desktop (macOS):** script Python sinh draft CapCut 9.5, mở và sửa tiếp trong CapCut.

## Gallery

| | Template | Loại | Khung · độ dài | Nội dung |
|---|---|---|---|---|
| <img src="gallery/spotlight_916_cover.jpg" width="160"> | **[Spotlight Reveal](spotlight_916/)** | HyperFrames | 9:16 · 11,5 s | Đèn rọi tự lắp ráp, quét chùm sáng làm lộ 4 dịch vụ rồi logo và handle. Chữ mono kiểu công nghệ, chỉ dùng SFX |
| <img src="gallery/travel_cinematic.jpg" width="160"> | **[Travel Cinematic](travel_cinematic/)** | CapCut | 16:9 · 22,5 s · 14 clip | Mở bằng dải dọc theo phách, chữ LOCATION đỏ, thẻ tiêu đề "Moments", montage theo beat 120 BPM, tông teal–cam |
| <img src="gallery/welcome_travel.jpg" width="160"> | **[Welcome Travel Moment](welcome_travel/)** | CapCut | 16:9 · 25,5 s · 52 clip | WELCOME đổi font từng nhịp, letterbox mở dần, tiêu đề Didone, khung lồng bật nấc, cuộn dọc, cắt theo phách 133 BPM |

### Spotlight Reveal (9:16)

![Spotlight Reveal](gallery/spotlight_916.jpg)

### Travel Cinematic (16:9)

![Travel Cinematic](gallery/travel_cinematic.jpg)

### Welcome Travel Moment (16:9)

![Welcome Travel Moment](gallery/welcome_travel.jpg)

_Ảnh của hai template CapCut là bản dựng gần đúng từ `draft_info.json` (`gallery/make_capcut_preview.py`), nên không có mask, filter,
hiệu ứng và chuyển cảnh. Ảnh Spotlight chụp thẳng từ HyperFrames._

## Dùng nhanh

### HyperFrames

```bash
cd spotlight_916
npx hyperframes preview          # mở Studio, sửa chữ ở bảng Variables
npx hyperframes render -o renders/spotlight_916.mp4
```

Cần Node.js và Chrome. Phiên bản HyperFrames được ghim trong `package.json`. Chi tiết: [spotlight_916/README.md](spotlight_916/README.md).

### CapCut (macOS, CapCut Desktop 9.5)

```bash
python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python travel_cinematic/make_placeholders.py      # clip màu giữ chỗ để xem bố cục
# ĐÓNG CapCut trước khi sinh draft
.venv/bin/python travel_cinematic/build_template.py --name "Da Nang Trip" \
    --clips c01.mp4 ... c14.mp4 --location "DA NANG" --music nhac.mp3
```

Mỗi template có README riêng, gồm bảng phân tích video gốc → cách dựng, các tham số, và cách khớp beat theo nhạc.
`travel_cinematic/draft_check.py` kiểm tra draft sau khi sinh. `tools/capcut-cli` (ghim bản 0.31.1) dùng để lint draft:
chạy `npm ci --prefix tools/capcut-cli` để cài.

## Cấu trúc

```
spotlight_916/        HyperFrames: index.html + compositions/ + assets/sfx/
travel_cinematic/     CapCut: build_template.py, beats.py (đo BPM), draft_check.py, stock/credits.tsv
welcome_travel/       CapCut: build_template.py (dùng chung write_draft, beats của travel_cinematic)
research/             Ghi chép phân tích reel mẫu + script đo khung hình (measure.py, tile.py, preview_draft.py)
gallery/              Ảnh xem trước + script dựng ảnh
tools/capcut-cli/     package.json ghim capcut-cli (chỉ dùng để lint)
BAO_CAO_CAPCUT_TEMPLATE.md   Ghi chép định dạng draft CapCut 9.5 macOS và cách sinh template
```

## Không có trong repo

| Thứ | Lý do | Lấy lại |
|---|---|---|
| 14 clip Pexels của bản demo | Giấy phép Pexels không cho đăng lại nguyên bản | `sh travel_cinematic/stock/download_stock.sh` (nguồn, tác giả ở `credits.tsv`) |
| 4 bài nhạc Mixkit | Giấy phép Mixkit Free cấm phân phối lại | Dùng nhạc của bạn (`--music`) |
| Clip giữ chỗ | Tạo lại được | `make_placeholders.py` trong từng template |
| Video, khung hình reel mẫu | Nội dung của tác giả khác, chỉ dùng để phân tích | Xem link nguồn trong README từng template |

Bản demo `welcome_travel` trong README dùng `travel_cinematic/stock/*.mp4`. Hãy tải stock trước hoặc thay bằng clip của bạn.

## Giấy phép tài nguyên

- SFX trong `spotlight_916/assets/sfx/` lấy từ Pixabay (Pixabay Content License, dùng thương mại không cần ghi nguồn).
  `whoosh-b`/`whoosh-c` là bản đổi tốc độ của `whoosh.mp3`.
- Font: HyperFrames dùng JetBrains Mono, Space Mono (Google Fonts, OFL). CapCut dùng font miễn phí có sẵn trong CapCut.
