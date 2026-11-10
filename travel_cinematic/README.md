# Template "Travel Cinematic" (dựng lại theo reel Srm Template)

![Travel Cinematic](../gallery/travel_cinematic.gif)

_GIF dựng gần đúng từ draft (font thay thế, chưa có animation chữ chi tiết)._

Nguồn tham khảo: https://www.facebook.com/reel/1863922174979264. Template gốc có 14 clip, khung 16:9, dài 22,5 giây.
Bản này dựng lại **bố cục, nhịp cắt và kiểu chữ**. Không dùng lại video hay nhạc của tác giả.

## Phân tích video gốc → cách dựng trong CapCut

| Thời gian | Video gốc | Bản dựng (`build_template.py`) |
|---|---|---|
| 0–4,6 s | Nền đen; mỗi phách hiện thêm một dải dọc (8 dải, mỗi dải rộng 1/8 khung) kèm chớp trắng | Ảnh đen trên track chính + 8 track video có mask chữ nhật rộng 1/8, cách nhau 1 phách (0,5 s); chớp trắng 2 khung hình cùng mask |
| 4,6–6,1 s | Chữ "LOCATION" sans hình học rất đậm, đỏ thẫm trong suốt (thấy cảnh phía sau), rộng ~62% khung | Poppins Bold cỡ 29, màu (0.80, 0.10, 0.13), độ đục 75%, outro *闭幕* khép cùng khung |
| 5,1–6,1 s | Viền đen khép từ trên và dưới vào | Hiệu ứng *闭幕* (Close) |
| 6,1–6,6 s | Đen, rồi chớp trắng | Nền đen + chớp trắng toàn khung 2 khung hình |
| 6,6–8,25 s | Cầu cảng + "Moments / from the Journey" + dòng phụ trên và dưới | Clip 8 zoom nhẹ; "TRAVEL" đậm + "CINEMATIC" mảnh (Montserrat); tiêu đề Gloock trắng 90%; phụ đề Gloock trắng với chữ cái đầu mỗi từ là Pinyon Script vàng chanh (text nhiều kiểu, class `RichText`); dòng phụ Montserrat |
| 8,25–8,6 s | Lướt nhanh 5 cảnh, mỗi cảnh 2 khung hình | Clip 10–14, mỗi clip 2 khung hình |
| 8,6–20,6 s | Montage 2 phách/cảnh, theo beat (~120 BPM) | 12 cảnh (clip 1–7, 9–13), zoom 1.0→1.05 |
| 20,6–21,1 s | Hai cảnh nhấp nháy xen kẽ | Clip 13/14 luân phiên, mỗi lần 2 khung hình |
| 21,1–22,8 s | Hoàng hôn + "thank you for everything" | Clip 14 zoom 1.0→1.1, chữ giãn rộng, mờ về đen (*渐隐闭幕*) |
| Toàn bộ | Tông teal–cam điện ảnh | Filter *青橙* (Teal orange) 50% |

Mọi hiệu ứng, font và filter dùng ở đây đều là loại **miễn phí** trong CapCut.

## Cách dùng

```bash
# 1. (một lần) tạo 14 clip giữ chỗ để xem bố cục
.venv/bin/python travel_cinematic/make_placeholders.py

# 2. ĐÓNG CapCut, rồi sinh draft
.venv/bin/python travel_cinematic/build_template.py --name "Da Nang Trip" \
    --clips c01.mp4 c02.mp4 ... c14.mp4 --location "DA NANG" --music nhac_120bpm.mp3
```

- Không truyền `--clips` thì script dùng clip giữ chỗ trong `placeholders/`.
- Clip dọc hoặc có tỉ lệ khác 16:9 sẽ tự được phóng to để phủ kín khung. Clip quá ngắn (dưới ~6,3 s với clip 1)
  sẽ tự làm chậm lại.
- **Media được chép vào `~/Movies/CapCut/Template Media/<tên draft>/`** (hard link, không tốn thêm dung lượng nếu cùng
  ổ đĩa). CapCut trên Mac chạy sandbox của App Store nên chỉ đọc được file trong `~/Movies`; file ở `~/Documents` hay
  `~/Downloads` sẽ hiện "Media chưa liên kết". Đổi chỗ bằng `--media-root`.
- Không được trùng tên draft đã có: đổi `--name` hoặc xoá draft cũ trong CapCut trước.
- Script tự đăng ký draft vào `root_meta_info.json` và sao lưu file cũ (`.bak_<timestamp>`).
- **Khớp beat tự động:** khi có `--music`, script đo BPM và pha beat (`beats.py`, dùng ffmpeg + numpy), rồi giãn toàn
  bộ timeline theo tỉ lệ 120/BPM để mỗi cảnh montage dài đúng 2 phách. `--music-at <giây>` chọn đoạn nhạc
  (ví dụ điệp khúc) rơi đúng lúc bắt đầu montage; script tự làm tròn về beat gần nhất.
- Mốc thời gian đã được lượng tử hoá theo lưới phách (cách 0,5 s ở 120 BPM). Các mốc đo từ video gốc bị trôi dần.

## Kiểm tra draft sau khi sinh

`write_draft()` tự chạy `draft_check.py` sau khi ghi (chỉ đọc, không sửa draft). Các script khác dùng `write_draft()`, như
`make_quahd_capcut.py`, cũng được kiểm tra. Truyền `check=False` để tắt.

```bash
.venv/bin/python travel_cinematic/draft_check.py "QUAHD Doc 9x16" "Travel Cinematic Demo v3"   # kiểm tra draft có sẵn
.venv/bin/python travel_cinematic/draft_check.py --strict --info <thư mục draft>              # có lỗi thì thoát mã 1
```

- **Kiểm tra riêng:** bản gốc `draft_info.json` phải giống hệt bản trong `Timelines/<id>/` (CapCut 9.x đọc bản lồng bên
  trong). Media phải tồn tại và nằm trong `~/Movies`. Draft phải có trong `root_meta_info.json`.
- **capcut-cli** ([renezander030/capcut-cli](https://github.com/renezander030/capcut-cli), cài ghim bản 0.31.1 ở
  `../tools/capcut-cli`): `lint` + `diagnose`, cảnh báo cả khi CapCut đang mở. Cài lại bằng
  `npm install --prefix tools/capcut-cli --ignore-scripts --save-exact capcut-cli@0.31.1` (chạy ở thư mục `capcut/`).
  Không có capcut-cli thì chỉ chạy phần kiểm tra riêng.
- **Đã lọc các cảnh báo không đúng với CapCut 9.5 Mac** (`IGNORED` trong `draft_check.py`):
  - `media-outside-draft`, `media-unlinked`, `media-unregistered`: media ở `Template Media/` vẫn mở tốt trên 9.5.
  - `keyframe-trimmed-clock`: chỉ áp dụng cho Jianying 11.6.
  - `main-track-gap`: chỉ bỏ qua khi draft tắt nam châm track chính (`maintrack_adsorb=False`).
  - `dangling-companion-ref` trên text segment: pyCapCut gắn id speed không có material; CapCut tự bỏ khi lưu.
- Mục `info` bị ẩn mặc định. Đó là id font, id hiệu ứng không có trong bảng của capcut-cli và mask ghi ở cả hai mảng;
  cả ba đều vô hại trên 9.5. Xem bằng `--info`.
- Cảnh báo `caption-too-fast` / `line-too-long` ở dòng "Some journeys end…" là do thiết kế: dòng phụ chỉ hiện ~1 s như
  reel gốc.

## Bản demo dùng tài nguyên miễn phí

```bash
.venv/bin/python travel_cinematic/build_template.py --name "Travel Cinematic Demo v2" \
    --clips travel_cinematic/stock/clip_*.mp4 --music travel_cinematic/music/mixkit_443.mp3 \
    --music-at 16.3 --location "CALIFORNIA"
```

- **Video:** 14 clip Full HD từ Pexels (giấy phép Pexels: miễn phí, cả thương mại, không bắt buộc ghi nguồn). Danh sách
  tác giả và link ở `stock/credits.tsv`.
- **Nhạc:** "Serene View" (Arulo, Mixkit, ~118 BPM, `music/mixkit_443.mp3`), theo Mixkit Stock Music Free License:
  được dùng trong video mạng xã hội và quảng cáo, không được đăng ký Content ID.
  `music/` còn 3 bài dự phòng: 13 "Summer Fun", 953 "Feel Alive", 963 "Just Keep Walking".
- **Lưu ý khi đăng template công khai:** người dùng template sẽ dùng lại bài nhạc, tức là phân phối lại. An toàn nhất
  là thay bằng nhạc trong thư viện CapCut (Audio → Music) trước khi *Share as Template*.

## Đăng thành template CapCut chính thức
CapCut Desktop không đánh dấu clip thay thế được. Cách làm: mở draft trên Desktop, chỉnh nhạc và kiểm tra, bật đồng bộ
cloud. Sau đó mở bằng CapCut Mobile hoặc capcut.com → *Share as Template* → đánh dấu 14 clip thay thế (cần tài khoản
Template Creator).
