# Template "Welcome Travel Moment" (dựng lại theo reel của Vindhx CapCut)

Nguồn tham khảo: https://www.facebook.com/reel/2054401788599994 ("New Template || Welcome Travel Moment"). Reel là bản
quay màn hình trình sửa CapCut mobile. Phần xem trước 16:9 dùng 52 clip màu giữ chỗ "CLIPS 1…52", nên đo được chính xác
từng nhịp cắt. Bản này dựng lại **bố cục, nhịp cắt, chuyển động và kiểu chữ**. Không dùng lại nhạc của tác giả.
Video tải về chỉ để phân tích, nằm ở `../research/reel_2054401788599994/` (không phân phối lại).

## Phân tích video gốc → cách dựng trong CapCut

Thời gian tính theo nhạc gốc **133,44 BPM** (1 phách = 0,4496 s). Mọi mốc đều được đo từng khung hình (`research/scripts/measure.py`).

| Thời gian | Video gốc | Bản dựng (`build_template.py`) |
|---|---|---|
| 0–0,23 s | Màn đen | Ảnh đen trên track chính |
| 0,23–3,17 s | 16 cảnh, mỗi cảnh 5–6 khung hình. Khung mở như letterbox: dải ngang cao 13% → 50% (0,77 s) → toàn khung (1,64 s) | 16 cảnh × 0,1836 s. Hai ảnh đen trên/dưới có keyframe vị trí Y, nằm **trên** track chữ để chữ bị cắt theo dải hình như mẫu |
| 0,23–3,17 s | "WELCOME" vàng `#FCDB58` đổi font 2 lần mỗi cảnh (sans hẹp, chữ tay, serif Didone, marker), có viền tối mờ. Từ 1 s thu nhỏ dần 100% → 45% | 32 đoạn chữ, xoay vòng Bebas Neue / Amatic / Didot (co ngang 60%) / Permanent Marker / Anton / Oswald Light. Keyframe scale theo đường cong đo được |
| 3,17–3,40 s | 1 khung đen, rồi chớp trắng | Ảnh đen 1 khung + ảnh trắng có keyframe độ đục 0 → 1 → 0 |
| 3,2–12,8 s | "TRAVEL MOMENT" (serif Didone siêu hẹp, vàng) + "YOUR LOCATION" (serif trắng, giãn chữ). Thu nhỏ 123% → 100% đến 4,77 s, rồi đứng yên trên cảnh 17–20 | Didot cỡ 35 co ngang còn 36%; Cinzel cỡ 7, giãn chữ 4. Keyframe scale + vị trí Y để hai dòng cùng thu về tâm khung. Mờ dần 0,2 s ở cuối |
| 7,2–7,45 s | Lóe sáng ấm (light leak) chuyển từ cảnh 18 sang 19 | Chuyển cảnh *闪白* (chớp trắng) 0,27 s + hiệu ứng *胶片漏光* (lóe sáng phim). Cả hai miễn phí |
| 12,7–15,2 s | Khung lồng cảnh 21 có bóng mờ, bật to từng nấc 40→62→75→84→100%, mỗi nấc chớp trắng trên khung. Sau đó thu nhỏ 86→66→54% để lộ cảnh 22 | Track `pip` có keyframe scale (các mốc giữ/nhảy ở `PIP_A`). Bóng mờ là ảnh PNG làm mờ trên track `pip_shadow`. Chớp là ảnh trắng cùng scale với khung, dài 2 khung hình |
| 16,9–18,6 s | Nền cảnh 23, lần lượt bật khung cảnh 24 (58%), 25 (70%), 26 (83%), mỗi lần chớp đen/trắng | `PIP_B` + `PIP_B_FLASH` |
| 19,05–20,36 s | Cuộn dọc: cảnh 28→42 trượt từ trên xuống, mép giữa hai cảnh đi 0,39 khung mỗi khung hình (0,0877 s/cảnh) | Mỗi cảnh có keyframe Y +2 → 0 → −2 (đơn vị nửa khung), xen kẽ hai track `scroll_a`/`scroll_b`. Cảnh 42 nằm sẵn ngoài khung trên track chính để track chính liền mạch |
| 20,83–25,55 s | Cảnh 43–52, mỗi phách một cảnh, cuối hơi tối dần | 10 cảnh theo lưới phách. Cảnh cuối dài 1,5 phách, mờ về đen 0,3 s |

Không có filter màu toàn video. Mọi hiệu ứng, chuyển cảnh và font dùng ở đây đều **miễn phí** (đã kiểm tra `is_vip` trong pyCapCut).

## Cách dùng

```bash
# 1. (một lần) tạo 52 clip màu giữ chỗ để xem bố cục
.venv/bin/python welcome_travel/make_placeholders.py

# 2. ĐÓNG CapCut, rồi sinh draft. Thay <...> bằng đường dẫn thật (thư mục clip, file nhạc)
.venv/bin/python welcome_travel/build_template.py --name "Da Nang Trip" \
    --clips <thư mục clip>/*.mp4 --title "DA NANG" --location "VIET NAM" --music <file nhạc> --music-at 45

# Chạy thử ngay bằng clip + nhạc có sẵn trong project
.venv/bin/python welcome_travel/build_template.py --name "Da Nang Trip" \
    --clips travel_cinematic/stock/*.mp4 --title "DA NANG" --location "VIET NAM" \
    --music travel_cinematic/music/mixkit_953.mp3 --music-at 39
```

- **Số clip:** 1–52 file. Ít hơn 52 thì quay vòng (cảnh n dùng clip `(n-1) % số_clip`). Thứ tự quan trọng nhất:
  1–16 là intro chớp nhanh, 17–20 nằm dưới tiêu đề (nên chọn cảnh rộng, yên tĩnh), 21–26 là khung lồng,
  28–41 chỉ hiện ~0,09 s, 42–52 là đoạn theo phách.
- **Chữ:** `--welcome`, `--title`, `--location`. Đổi WELCOME sau khi sinh thì phải sửa cả 32 đoạn chữ. Sửa bằng script
  sẽ nhanh hơn.
- **Nhạc:** script đo BPM (`travel_cinematic/beats.py`) và giãn toàn bộ timeline theo tỉ lệ 133,44/BPM. `--music-at <giây>`
  chọn đoạn nhạc (ví dụ điệp khúc) rơi đúng mốc "drop" ở cảnh 43, nơi bắt đầu cắt theo từng phách.
- Clip không phải 16:9 sẽ được phóng to phủ kín khung, kèm mask chữ nhật để không lấn ra ngoài khi thu nhỏ hoặc trượt dọc.
- Media được hard link vào `~/Movies/CapCut/Template Media/<tên draft>/` (CapCut Mac chạy sandbox). Script tự đăng ký
  draft vào `root_meta_info.json` và sao lưu file cũ. Xem thêm ở README của `travel_cinematic/`, vì hai template dùng
  chung `write_draft()`.

## Draft đã sinh (28/10/2026)

| Draft | Nội dung | Thời lượng |
|---|---|---|
| `Welcome Travel Moment Template` | 52 clip màu giữ chỗ, đúng nhịp bản gốc, chưa có nhạc | 25,55 s |
| `Welcome Travel Moment Demo` | 14 clip Pexels của `travel_cinematic/stock/` (quay vòng) + "Feel Alive" (Mixkit 953, 150 BPM, `--music-at 39`) | 22,73 s |

Kiểm tra tự động (`draft_check.py`): 0 lỗi. Có 34 cảnh báo, đều do thiết kế: `caption-too-fast` ở 32 đoạn WELCOME (mỗi đoạn
92 ms, chính là hiệu ứng đổi font) và `cue-too-long` ở 2 dòng tiêu đề 9,6 s (tiêu đề, không phải phụ đề).

## Kiểm tra trước khi mở CapCut: dựng thử khung hình

`research/scripts/preview_draft.py` đọc `draft_info.json` (scale, vị trí, keyframe, độ đục, thứ tự track) và vẽ khung hình
gần đúng, đặt cạnh reel gốc cùng mốc thời gian:

```bash
.venv/bin/python -I research/scripts/preview_draft.py "<thư mục draft>" research/reel_2054401788599994/reel.mp4 so_sanh.jpg 0.5 3.3 13.1 19.2
```

Bản dựng thử khớp với reel ở độ cao dải letterbox, đường thu nhỏ WELCOME, kích thước và vị trí tiêu đề, từng nấc khung lồng
và hướng cuộn dọc. Công cụ này **không** vẽ đúng font, hiệu ứng, chuyển cảnh hay animation chữ.

## Cần xem lại trong CapCut (chưa kiểm chứng trên app)

1. **Thứ tự lớp của viền letterbox.** Hai track `bar_top`/`bar_bottom` có `render_index` cao hơn track chữ. Nếu CapCut vẫn
   vẽ chữ đè lên viền, WELCOME sẽ tràn ra ngoài dải hình ở 0,23–1,6 s. Khi đó kéo hai track viền lên trên track chữ.
2. **Font.** Tên font trong pyCapCut ánh xạ tới font CapCut theo id, nhưng chưa xem tận mắt. Nếu Didot co 36% trông quá mảnh,
   tăng `TITLE_SQUEEZE` (0,4–0,45) hoặc thử font hẹp sẵn (`Vogue`, `West_West_Condensed`).
3. **Cỡ chữ** tính theo hiệu chỉnh cũ (≈ 8 px mỗi đơn vị cỡ trên khung 1080p). Lệch thì sửa cỡ trong `WELCOME_FONTS`,
   cỡ của title/location.
4. **Scale ngang ≠ dọc trên chữ** (keyframe `scale_x`/`scale_y` riêng). JSON hợp lệ, nhưng chưa thấy CapCut hiển thị.

## Đăng thành template CapCut chính thức

Giống `travel_cinematic`: mở draft trên Desktop, thay nhạc bằng nhạc trong thư viện CapCut, bật đồng bộ cloud. Sau đó mở bằng
CapCut Mobile hoặc capcut.com → *Share as Template* → đánh dấu các clip thay thế (cần tài khoản Template Creator).
Nhạc Mixkit trong bản Demo chỉ dùng để xem thử. Template công khai sẽ phân phối lại bài nhạc, nên phải thay nhạc trước khi đăng.
