# Thư viện media cho stock clip và nhạc: chỉ mục, tìm không dấu, `@tên`

_Ngày: 2026-11-06 · Học từ Quick Share 0.1.32 (đọc tĩnh mã, 06/11/2026); chưa chạy thật_

Ghi chú cách làm, chưa có script. Không chép mã của Quick Share, chỉ ghi cách làm và thông số để tự viết.
Nguồn: `~/Documents/Mmo/Gamiauto Browser/quick-share-research/PHAN-DUNG-DUOC.md` §7.

## Vì sao cần

- Stock hiện nằm rải trong template:
  - 14 clip Pexels ở `travel_cinematic/stock/` (`clip_01.mp4` … `clip_14.mp4`); tác giả, tiêu đề, link ở
    `credits.tsv`;
  - 4 bài Mixkit ở `travel_cinematic/music/` (`mixkit_<id>.mp3`).
- Tên file không nói gì về nội dung. Muốn chọn clip theo cảnh thì phải tra `credits.tsv` hoặc mở từng file.
- `build_template.py` nhận `--clips` theo đường dẫn và **theo thứ tự**. Ở `welcome_travel`, thứ tự quyết định clip rơi vào
  cảnh nào (1–16 intro, 17–20 dưới tiêu đề, 21–26 khung lồng…).

## 1. Chỉ mục

Một file JSON. Mỗi mục:

| Trường | Nội dung |
|---|---|
| `id` | `sha256(đường dẫn)` |
| `path` | Đường dẫn file |
| `size` | Kích thước |
| `mtime` | Thời điểm sửa file |
| `duration` | Thời lượng |
| `tags` | Nhãn |
| trạng thái "mất" | Kèm thời điểm thấy mất, để tính 7 ngày |

- Quét thư mục nguồn **sâu 1 cấp**, gọi stat theo lô.
- File biến mất thì đánh dấu "mất". Sau **7 ngày** mới xoá khỏi chỉ mục.
- Vì `id` tính từ đường dẫn, đổi tên hay chuyển file sẽ thành mục mới, còn mục cũ thành "mất".

## 2. Tìm kiếm

- Chuẩn hoá **cả câu tìm lẫn tên file** theo đúng thứ tự:
  1. NFD;
  2. bỏ dấu (ký tự U+0300–U+036F);
  3. đ/Đ → d;
  4. chữ thường.

  Ví dụ: "Bãi Biển Đà Nẵng" → "bai bien da nang".
- Phân trang bằng con trỏ: trang sau bắt đầu ngay sau mục cuối của trang trước.

## 3. Xoá

- Chỉ chuyển vào **Thùng rác** của macOS, không xoá hẳn.
- Không cho xoá:
  - file đang dùng, tức là file mà một draft đang trỏ tới (`materials.*.path` trong `draft_info.json`). Tính cả bản hard
    link trong `~/Movies/CapCut/Template Media/<tên draft>/`;
  - file nằm ngoài thư mục nguồn của thư viện.

## 4. `@tên`

- Đặt tên ngắn cho từng mục, ví dụ `@bai_bien`, `@cau_cang`, `@hoang_hon`.
- Ở Quick Share, `@tên` dùng khi dựng prompt cho model AI:
  - thay `@tên` bằng một mô tả ngắn, **≤120 ký tự mỗi tên, ≤400 ký tự cả prompt**;
  - đính file theo **đúng thứ tự xuất hiện**.
- Dự án này chưa có bước dựng prompt (hiệu ứng AI của CapCut chỉ dùng tay trong app), nên phần thay mô tả chưa dùng tới.
  Phần dùng được ngay là thứ tự: `--clips @a @b @c` giải ra đường dẫn đúng theo thứ tự đã ghi.

## Áp dụng vào dự án này

1. **Thư mục nguồn:** `travel_cinematic/stock/` và `travel_cinematic/music/`, cộng thư mục stock mới nếu sau này thêm.
   - Không quét `~/Movies/CapCut/Template Media/`. Đó là bản hard link cho từng draft; đường dẫn khác nên `id` khác,
     sẽ thành mục trùng.
2. **Thời lượng** đọc bằng ffprobe (ffmpeg đã dùng ở `travel_cinematic/beats.py`).
3. **Nhãn ban đầu:**
   - clip Pexels: lấy cột `title` và `author` của `credits.tsv`;
   - nhạc: tên bài ghi trong `travel_cinematic/README.md` ("Serene View", "Summer Fun", "Feel Alive",
     "Just Keep Walking"), cộng BPM đo bằng `beats.py`.
4. **Tìm theo nhãn:** tên file là `clip_01.mp4`, `mixkit_443.mp3` nên tìm theo tên không ra gì. Áp cùng phép chuẩn
   hoá ở mục 2 cho nhãn và tìm cả trong nhãn.
5. **Script:** đặt cạnh `beats.py` và `draft_check.py` trong `travel_cinematic/`, vì `welcome_travel` cũng dùng chung
   các hàm ở đó. Lệnh tối thiểu: quét, tìm, xoá vào Thùng rác.
6. **`@tên` trong `--clips` và `--music`** của hai `build_template.py`: tham số bắt đầu bằng `@` thì tra chỉ mục ra đường
   dẫn, giữ nguyên thứ tự. Tên không có trong chỉ mục thì dừng và báo lỗi, giống chỗ script đang báo file không tồn tại.
7. **Kiểm "đang dùng" trước khi xoá:** đọc các draft như `draft_check.py` đang làm (`materials.*.path`). Chưa đọc được
   draft thì không xoá.
