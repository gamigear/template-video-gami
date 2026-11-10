# 11 · Bản triển khai tham chiếu (mã đã chạy thật) và cách mang sang repo khác

Mọi đường dẫn dưới đây tính từ `FS/` = `/Users/dteanh/Projects/Fisoft` (ổ trong). Từ 06/11/2026, đây **chỉ là bộ công cụ video** chép từ repo FiSoft: `output/reels` (tài liệu, `_khuon`, `_mau-*`, `_tools`, `_audio`, `_base`, `content`) và `output/motion/fisoft-motion-kit-v1`. Các phần khác của repo (phim-nhan-vat, Kịch bản, brand, thư mục từng reel) chỉ còn trên SSD Crucial đã tháo, `/Volumes/Crucial SSD/Fisoft`. Đường dẫn nào không có thì dùng sổ tay này (đã đủ luật + lệnh) và viết lại. Đường dẫn có trong `FS/` thì **đọc mã gốc trước khi viết lại** — rẻ hơn nhiều.

## 1. Tài liệu gốc (nguồn của sổ tay này)

| File | Nội dung |
|---|---|
| `FS/output/reels/CLAUDE.md` | luật dự án reel: §3c âm thanh, §3d bảng số chuyển động, §4 quy trình, §5b bảng bẫy, §5c three.js |
| `FS/output/reels/HOC-HOI-SKILL-VIDEO.md` | phân tích ~40 nguồn (mục 1–14): mượn gì, bỏ gì, vì sao |
| `FS/output/reels/NGHIEN-CUU-GSAP.md` | plugin GSAP: cái nào tất định, cách dùng trong HyperFrames |
| `FS/output/reels/NGHIEN-CUU-SFX-QUA-HD.md` | SFX hook cao, đo bộ SFX, giấy phép |
| `FS/output/reels/QUY-TRINH-KICH-BAN-NOI-DAU.md` | quy trình viết kịch bản chuỗi "nỗi đau → giải pháp" |
| `FS/output/reels/REELS_BRIEF.md` | brief chuỗi reel sản phẩm |
| `FS/Kịch bản phim ngắn nhân vật/NGHIEN-CUU-QUY-TRINH-PHIM-AI.md` | quy trình phim AI (Flow/Omni), bộ lọc, chi phí |
| `FS/Kịch bản phim ngắn nhân vật/KINH-THANH-NHAN-VAT.md`, `TUYEN-THIEN-LINH.md` | mẫu kinh thánh nhân vật; nhật ký một tuyến phim 15 tập |
| `FS/output/reels/_khuon/<khuôn>/HUONG-DAN.md` | hướng dẫn + bẫy riêng từng khuôn |
| `FS/output/phim-nhan-vat/tl-1/hau-ky/HUONG-DAN.md` | hướng dẫn khuôn hậu kỳ phim AI |

## 2. Khuôn reel (HyperFrames)

Mỗi khuôn: `FS/output/reels/_khuon/<khuôn>/` gồm `compositions/` (HTML từng cảnh + `captions.html` + `nen.html`), `assets/` (GSAP, font woff2, `brand.css`), `script/{voice.mjs, build.mjs, render.mjs, mix-audio.py}`, `hyperframes.json`, `HUONG-DAN.md`; khuôn 3D thêm `src/` (esbuild → `assets/three-*.js`).

| Khuôn | Dùng làm mẫu cho |
|---|---|
| `contentta` | **mẫu chuẩn nhất**: build đo WAV, mốc `luc`, `LAND` chạm đất, phụ đề karaoke, bộ kiểm font, CTA tham số |
| `hanh-trinh-ho-so` | nguồn `mix-audio.py` đã vá treo `amix` (chép từ đây khi làm khuôn mới) |
| `luot-man-hinh` | camera + con trỏ trên ảnh chụp màn hình; **bộ lọc SFX theo ưu tiên + trần** (`script/build.mjs` khoảng dòng 147–259) |
| `so-do-giai-phap` | GSAP CustomEase + DrawSVG + MotionPath + MorphSVG đã duyệt |
| `chu-khoi-3d`, `thiet-bi-3d` | three.js trong HyperFrames: `buildReady`, tween đại diện, canvas texture, `src/lib.js` |
| `sa-ban-3d`, `sa-ban-3d-td` | thế giới 3D + chuỗi cú máy + phong cách cắm được; trang dev `dev/xem.html?t=` |
| `bang-chuyen`, `chu-dong-3-diem`, `demo-tuong-tac`, `man-hinh-may-tinh`, `truoc-sau-so-hoa` | các ý tưởng hình ở `07-hyperframes-khuon-bay.md` §7 |

Mẫu thử khác: `FS/output/reels/_mau-3d-moi/` (4 mẫu 3D + `DE-XUAT.md` + `_src/bang_so_sanh.py`), `FS/output/reels/_mau-gsap/` (so sánh trước/sau plugin GSAP).

**Âm thanh dùng chung:** `FS/output/reels/_audio/sfx-v2/` (bộ SFX đặt tên theo chức năng + `README.md` nguồn/giấy phép + `_do.json` số đo đỉnh/attack), `_audio/sfx/` (bộ cũ, gồm `hook-cao.wav`), `_audio/bgm/bed-src.wav`. Giấy phép một số file là **cá nhân, cấm phát tán lại** → repo khác phải tự tải từ trang gốc, không chép file.

## 3. Công cụ kiểm (`FS/output/reels/_tools/`)

| Công cụ | Chạy | Phụ thuộc | Mức tổng quát |
|---|---|---|---|
| `scriptcheck.mjs` | `node _tools/scriptcheck.mjs content/<mã>.json [--pace 0.29] [--json out]` | Node ≥ 18, không gói | phần đếm âm tiết, ước thời lượng, sàn/trần cụm, regex biên từ Unicode `(?<![\p{L}\p{N}])` dùng lại được; danh sách từ cấm, câu CTA, luật mã sản phẩm là của FiSoft |
| `readcheck.mjs` | `node _tools/readcheck.mjs <thư-mục> [--dump t1,t2] [--no-font]` | hàm **nội bộ** của HyperFrames 0.8.159 trong cache npx (`HF_DIST` để ghi đè) | mọi dự án HyperFrames; gãy khi đổi phiên bản HyperFrames; không đọc chữ canvas/WebGL |
| `asr_check.py` | `_tools/.venv/bin/python _tools/asr_check.py <thư-mục> [--threshold 0.92]` | venv: faster-whisper 1.2.1, ctranslate2, soundfile, soxr, numpy; model large-v3-turbo tải từ HF lần đầu | tổng quát (đổi ngôn ngữ, từ điển tên riêng) |
| `timeline_view.py` | `_tools/.venv/bin/python _tools/timeline_view.py <thư-mục> [--at t1,t2]` | Pillow, numpy, ffmpeg; đọc `captions.json`, `build/timeline.txt`, `build/cues.json` | tổng quát nếu build sinh cùng định dạng; sửa regex mã video + đường dẫn font macOS |
| `drive-upload.mjs` | `node _tools/drive-upload.mjs <file.mp4> \| --all \| --status` | macOS, app Google Drive cho máy tính; cấu hình `drive.json` | ghi `.part` rồi đổi tên, chờ xattr `com.google.drivefs.item-id#S` hết "local" (≤ 600 s), dọn cache |
| `test/` | ca đối chứng âm + README | | quy ước mỗi kiểm một ca cố ý sai |

## 4. Hậu kỳ phim AI (`FS/output/phim-nhan-vat/`)

| Script | Chức năng |
|---|---|
| `_tools/kiem-clip.py` | ảnh ghép kiểm clip, phát hiện lặp/cắt cảnh/tiếng nền, chấm 6 tiêu chí → `BAO-CAO.md` (cần whisper-cli + ggml-small) |
| `_tools/che-loi.py` + `<tập>/hau-ky/che-loi.json` | vá nền / làm mờ / cắt + chớp theo đặc tả; lệnh `mau` xuất ảnh trước/sau |
| `tl-1/hau-ky/tg.py` | trục thời gian sau khi cắt (`at(c, t)`) |
| `tl-1/hau-ky/thay-man-xanh.py` | bám 4 góc màn xanh, homography, khử ánh xanh |
| `tl-1/hau-ky/cat-lap.py` | cắt lặp + punch-in neo watermark |
| `tl-1/hau-ky/build.py` + `noi-dung.json` + `phu-de.json` + `moc.json` | sinh composition HyperFrames (clip, chữ, thẻ, phụ đề có tên vai, end card) |
| `tl-1/hau-ky/mix.py` | chuẩn hoá thoại từng clip, nhạc 3 đoạn + sidechain, SFX căn đỉnh, `alimiter`, −14 LUFS. Đã vá treo `amix` 02/11/2026 (cả 21 bản `*/hau-ky*/mix.py`; tl-1, tl-1-3d, tl-6 chạy lại khớp bản giao ±2 LSB). Còn sót mẫu cũ: `FS/output/reels/HC-14-bai-do/script/mix-audio.py` (bản riêng một reel, không phải khuôn) |
| `tl-1/hau-ky-3d/build.py` | biến thể chèn PiP |
| `tap-7/chen-3d/ghep.py`, `kiem-noi.py` | chèn trọn video giải pháp giữa phim (xfade/acrossfade) + kiểm mối nối |
| `_chung/thuong-hieu/dong-dau.py` + `QUY-CACH-V2.md` | delogo + đóng dấu; quy cách logo đã duyệt |
| `_tools/gen.py` + `jobs-*.json`, `_tools/khoi-mo-ta.json` | tạo ảnh hàng loạt bằng Codex CLI (`stdin=/dev/null`); khối mô tả nhân vật |
| `tl-11/_tools/prompts.py`, `flow_prompts.py`, `flow-inject.js`, `helper2.js`, `kiem.py`, `lay.sh`, `nhan.sh` | mẫu prompt HEAD/END/EDIT, gói prompt Flow, chèn prompt vào ô soạn, kiểm/nhận/lấy khung |
| `_tools/muse-batch.js` (dễ gãy), `_tools/nhan-anh.py` (**không dùng được**) | ghi lại để khỏi thử lại |

## 5. Phụ thuộc hệ thống

- ffmpeg/ffprobe (tone-map HDR cần bản có `libzimg`; Homebrew mặc định không có), Node ≥ 18, Python 3 + numpy + Pillow.
- `npx --yes hyperframes@0.8.159` (ghim phiên bản), Chromium do HyperFrames tải.
- GSAP 3.15 (file cục bộ trong `assets/`), three r186 + esbuild (khuôn 3D).
- faster-whisper (venv) cho ASR từng câu; whisper-cli + `ggml-small.bin` cho kiểm clip AI.
- VieNeu TTS server `127.0.0.1:23334` (giọng tiếng Việt). Từ 04/11/2026 server chạy trên mbp2016; M1 nối tới qua
  đường hầm SSH nên địa chỉ không đổi.

## 6. Cách mang sang repo mới

1. **Đọc `SKILL.md` của sổ tay**, chọn quy trình (reel lời đọc / phim AI / video thật).
2. Có ổ FiSoft: chép khuôn gần nhất (`contentta` cho reel 2D, `chu-khoi-3d` cho 3D) + `_tools/` + `mix-audio.py` của `hanh-trinh-ho-so`. Không có: dựng từ `07` §1 và `12`.
3. **Thay phần riêng FiSoft**: `brand.css` (màu, font), từ cấm + câu CTA trong `scriptcheck`, `drive.json`, logo, regex mã video trong `timeline_view.py`, `initial_prompt` tên riêng trong `asr_check.py`.
4. Giữ nguyên các luật cứng (`SKILL.md` §3) và các vá đã biết (treo `amix`, kiểm font, neo chống khung đen).
5. Viết `CLAUDE.md` cho repo mới: ghi luật riêng của dự án, trỏ về sổ tay này cho phần chung.
6. Bài học mới ở repo mới → ghi ngược vào sổ tay này (`SKILL.md` §6).

## 7. Chọn máy render: M1 hay mbp2016 (từ 05/11/2026)

- **Máy:** mbp2016 là MacBook Pro 2016 Intel, 16 GB RAM, làm server phụ qua Tailscale. Đã cài Node, ffmpeg và
  Chrome của HyperFrames. Chi tiết máy và số đo nằm trong repo `gamigear-tech-studio`.
- **Khi nào hỏi:** trước mỗi lần render bản cuối hoặc render theo lô, hỏi người dùng render trên máy nào. Gộp vào câu
  xin duyệt render (§3 luật 1).
- **So sánh (đo 05/11/2026, 3 dự án thật):**
  - mbp2016 chậm hơn M1 1,8–2,3 lần. Reel Fisoft 41 s: 137 s so với 60 s. Footage Minigame 91 s: 345 s so với 192 s.
  - Hình ra trùng khớp, SSIM ≥ 0,986. three.js chạy bằng GPU Intel (ANGLE Metal).
  - Khi render, M1 đã swap 1,8 GB; mbp2016 còn trên 82% RAM trống.
  - **Chọn mbp2016:** lô dài, hoặc M1 đang bận việc khác.
  - **Chọn M1:** cần gấp.
- **Dự án HyperFrames bất kỳ:** đứng trong thư mục dự án, chạy `hf-render-mbp -o renders/<tên>.mp4 [-- <tham số render>]`.
  - Bản hyperframes đọc từ `package.json`. Nếu không ghim, truyền `--hf hyperframes@X.Y.Z`.
  - Lệnh chép dự án sang mbp2016, bỏ qua `renders/`, `node_modules/` và MP4/MOV ở gốc mà HTML không dùng. Lần sau chỉ
    chép phần đã đổi.
  - Render chạy `nice 10` và mỗi lúc một job. MP4 chép về đúng đường dẫn `-o`.
  - Ctrl-C dừng cả job trên mbp2016.
- **Khuôn Fisoft:** thêm cờ `--mbp` vào lệnh `render.mjs`. Chỉ bước render chạy trên mbp2016; kiểm, loudnorm và upload
  vẫn chạy trên M1.
  - Mang sang repo khác: chép `_tools/render-may.mjs`, thay lệnh `npx hyperframes render` bằng
    `renderHF(dir, HF, out, flags, args)`.
- **Vẫn chạy trên M1:** preview, studio, `snapshot`, `hyperframes check`. Đây là việc tương tác, cần nhanh.
- **mbp2016 không kết nối được:** lệnh dừng và báo lỗi, không tự chuyển sang M1. Hỏi lại người dùng.
- **Mã nguồn lệnh:** `gamigear-tech-studio/cong-cu/render-mbp2016/`, bản chạy được cài ở `~/.local/bin/hf-render-mbp`.
