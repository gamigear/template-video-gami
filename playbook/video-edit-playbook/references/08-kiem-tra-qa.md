# 08 · Kiểm tra chất lượng (QA) trước khi đưa người duyệt

Nguyên tắc: **Claude không xem được video và không nghe được tiếng** → mọi thứ phải đo trên **file giao** (MP4 cuối, không phải nguồn), có con số, có ảnh kiểm. Báo cáo ghi rõ "chỉ đo, chưa nghe/chưa xem chạy" và giao mốc cụ thể cho người.

## 1. Thứ tự chạy

| # | Lúc | Kiểm | Công cụ (bản tham chiếu `11-trien-khai-tham-chieu.md`) |
|---|---|---|---|
| 1 | trước TTS | kịch bản: âm tiết, thời lượng ước tính, câu dài, hook, vị trí lộ diện, từ cấm, số, CTA, cụm phụ đề | `scriptcheck.mjs` |
| 2 | sau TTS | ASR so lời; LUFS từng câu; ngừng thật giữa câu | `asr_check.py`, `ebur128`, cột "ngừng thật" của build |
| 3 | sau build | lint/kiểm tĩnh; thời gian giữ chữ trên hình + font đã tải | `hyperframes check`, `readcheck.mjs` |
| 4 | sau build | ảnh khung giữa mỗi cảnh, tự xem bố cục | `hyperframes snapshot` |
| 5 | sau render | ảnh ghép khung + sóng + từ + mốc tại mỗi ranh giới cảnh ±1,5 s; RMS theo cảnh | `timeline_view.py` |
| 6 | sau render | strip 10 khung quanh mỗi mốc cắt; khung đen; khung phẳng; khung nháy; khớp vòng | ffmpeg (`12-lenh-ffmpeg.md` §2) |
| 7 | sau render | tương phản sau từng cụm phụ đề | đo pixel trên khung render |
| 8 | sau render | phone sheet 360 px + 200 px | ffmpeg tile |
| 9 | sau render | LUFS/TP stereo + mono; SFX nghe được; CTA không chìm | `12-lenh-ffmpeg.md` §4 |
| 10 | trước khi giao | agent phê bình (chỉ đọc, mặc định bác bỏ) + agent mới tóm tắt thông điệp | §5 |

Ngay sau render (hypit làm bắt buộc; FiSoft có `_tools/mp4check.mjs` từ 02/11/2026, chỉ báo): ffprobe đúng 1 luồng H.264 + 1 luồng âm, đúng kích thước, đúng fps, **số khung = ceil(tổng giây × fps)** (HyperFrames làm tròn lên; dùng round sẽ báo thừa 1 khung ở phần lớn video), âm − hình trong −1 khung … +0,1 s (sau loudnorm/AAC âm dài hơn 0–0,067 s do đệm khung 1024 mẫu), 48 kHz; nhãn màu BT.709 + `+faststart` (đọc thứ tự hộp moov/mdat ở đầu file). Kèm ca đối chứng: làm 4 bản cố ý hỏng (cắt 1,1 s, bỏ âm, đổi cỡ, bỏ faststart) và kiểm phải bắt đủ.

Tối đa **3 vòng** sửa → render → kiểm. Còn lỗi thì báo người dùng (lỗi gì, mốc nào, bằng chứng), không lặp tiếp.

`hyperframes check` trước render (đã thử 02/11/2026 trên 3 reel đã duyệt, FiSoft `_tools/hfcheck.mjs`, `render.mjs` gọi ở chế độ chỉ báo):
- Dùng `--json --frame-check`, **chạy bằng GPU thật**. `--no-browser-gpu` (SwiftShader) cho cùng kết quả nhưng chậm gấp 4, còn reel three.js thì quá hạn sau 146 s. Với GPU chỉ mất 12–18 s mỗi reel.
- **Không dùng `--at-transitions`**: reel có tween cho từng từ phụ đề bị quá hạn sau 2,5 phút; khuôn có chuyển cảnh zoom thì báo nhầm nhiều.
- Lỗi thật đã bắt được: phụ đề chồng ở chỗ nối (03 §5).
- Báo nhầm: chữ tràn khung hoặc bị che đúng lúc đổi thẻ có chủ ý; nền trang trí tràn mép ở mức info.
- Check lấy mẫu thưa nên báo 0 chưa chắc là sạch.
- Chưa thử: `--caption-zone`, `--strict`. Có thể so SHA `index.html` trước/sau render để bắt file bị sửa giữa chừng.

## 2. Ngưỡng

**Kịch bản (video lời đọc 30–40 s):** 100–120 âm tiết; câu ≤ 20 âm tiết; câu hook ≤ 14 âm tiết, không tên thương hiệu, không mở bằng câu sáo ("bạn có biết", "hiện nay", "trong thời đại"…); câu lộ diện bắt đầu ở 30–50 % thời lượng, `nghi` trước nó ≥ 0,8 s; mọi chữ số phải nằm trong danh sách số được phép; câu CTA đúng nguyên văn đã chốt. Ước thời lượng = 0,35 + Σ(nghi + âm tiết × pace) + 1,75.

**Chữ trên hình (readcheck):** mỗi khối chữ phải có một lần hiện liên tục ≥ max(1,5 s, ký tự không trắng / 15 + 1,5 s). "Hiện" = độ mờ cộng dồn ≥ 0,5, nằm trọn khung và trong mọi cha có overflow, tâm không bị cảnh khác đè. Không thấy khối nào → lỗi chạy (không phải "đạt").

**Nhịp hình:**
- **Dead beat:** khe không có sự kiện hình > 2,2 s phải ghi lý do trong JSON (vd `"giu": "đọc bảng 3 dòng"`); không shot nào > 2,8 s mà không có chuyển động trong khung; > 3 s là lỗi.
- Strip đọc "chữ ký": nhảy rồi các ô y hệt = dừng chết; dừng rồi chuyển động khác = hai cử chỉ nên gộp; một ô khác hẳn hai bên = nháy.
- Mọi tween xong trước mốc cắt.

**Âm:** −14 ±0,5 LUFS, TP ≤ −1 dBTP trên file stereo giao; mono không lộ triệt pha; CTA không thấp hơn đoạn lời > 3 dB; SFX không to hơn lời; mỗi SFX đã thêm phải đo được (RMS dải tần trong cửa sổ quanh cue nhảy rõ so với nền).

**Phụ đề:** cụm 0,35–2,2 s, ≤ 6 từ / 8 âm tiết; tương phản đạt WCAG AA; tua tới `end + 0,01` không còn thấy cụm cũ.

**Định dạng:** `ffprobe` ra h264 high, yuv420p, tv, bt709, có AAC 48 kHz, faststart; 1080×1920; thời lượng đúng dự kiến ±0,1 s.

**Đuôi và khung chết (ngưỡng AIEVv2):** lặng đuôi = `silencedetect=noise=-45dB:d=0.6` trên 4 s cuối, > 1,2 s là lỗi (ffmpeg vẫn in `silence_end` ở EOF, nên tính từ `silence_start` cuối); khung đen `blackdetect=d=0.25:pic_th=0.98:pix_th=0.03`; đứng hình `freezedetect=n=-60dB:d=2`.

## 3. Kiểm hình bằng mắt (của agent)

- Chụp khung giữa mỗi cảnh + strip quanh mỗi cắt; **xem ảnh trước khi đưa người duyệt**.
- **Phone sheet** ở 360 px và **200 px** (cỡ ô reel khi lướt): chữ nào không đọc được ở đó là quá nhỏ.
- **Khung 0**: có chữ hook, không đen/trống/đang mờ vào.
- **Dấu tiếng Việt**: soi chữ hoa có dấu chồng ở tiêu đề (Ắ Ỗ Ữ) không bị cắt.
- **Test nhận diện**: 6 khung ngẫu nhiên, che chữ → vẫn nhận ra thương hiệu.
- **Hai cảnh kề nhau xem dạng bóng** (ẩn chữ) phải khác nhau; đảo độ sáng/bão hoà mỗi lần đổi cảnh.
- **Kiểm trùng thông tin**: lời và phụ đề đã mang chữ thì hình phải cho thấy ví dụ/quan hệ/hậu quả, không lặp lại chữ lần ba.
- Chi tiết nhỏ (ngón tay, kính, chữ trong ảnh) dễ báo nhầm trên ảnh lưới → phóng to vùng đó trước khi ghi lỗi.

## 4. Kiểm âm, và mốc giao người nghe

Đo theo `05-am-thanh-sfx.md` §8. Báo cáo kết thúc bằng **5 mốc nghe bằng tai nghe**: hook (0–1,5 s), riser → tiếng nhấn lộ diện, tiếng to nhất, cụm SFX dày nhất, CTA. Không bao giờ viết "nghe ổn".

## 5. Agent phê bình và agent đọc thông điệp

- **Agent phê bình** (subagent riêng, chỉ đọc, được dặn mặc định bác bỏ): xem ảnh kiểm + timeline + số đo; chấm từng cảnh /10; trả phán quyết, lỗi xếp hạng có timecode + bằng chứng, 5 việc sửa trước. Cảnh < 8 thì sửa.
- **Agent đọc thông điệp** (mới hoàn toàn, không đọc kịch bản): chỉ xem dãy khung → tóm tắt video nói gì, "người lạ biết gì trước giây 4". Tóm sai = video khó hiểu, sửa hình chứ không sửa lời giải thích.
- Clip AI: chấm **mù** trước (không đọc ghi chú), đối chiếu ghi chú sau (`09-phim-ai-hau-ky.md` §4).

## 6. Luật cho chính công cụ kiểm

- **Mỗi kiểm mới phải có ca đối chứng âm**: một file nội dung cố ý sai phải FAIL (phụ đề lệch 0,3 s, thiếu một từ, khe một khung, lặp cảnh). Kiểm không bắt được ca sai thì không chứng minh gì. Để chung trong `test/` + README.
- Mã thoát thống nhất: 0 đạt (có thể có cảnh báo) · 1 có lỗi · 2 không chạy được.
- Kiểm chạy trên **bản render**, không trên mã nguồn ("sửa code mà video không đổi" là bẫy thường gặp).
- Tua tất định: chụp cùng mốc theo 3 thứ tự khi sửa khuôn, ảnh phải giống từng byte (`07-hyperframes-khuon-bay.md` §2).
- Khi đổi mã dùng chung (bundle three, CSS chung): so khung trước/sau trên video đã render; sửa dọn mã phải ra 0 khác biệt.

## 7. Báo cáo cho người duyệt

```
<mã>: <thời lượng> s · <LUFS> LUFS / TP <x> dBTP (mono <y>) · readcheck <đạt/không> · ASR <ratio>
Ảnh kiểm: <đường dẫn verify/>
Cảnh yếu nhất: <cảnh> — <vì sao> — <cách sửa lần sau>
Chưa kiểm được: <ví dụ: chưa nghe; chưa xem trên điện thoại thật>
Mốc cần nghe: 0,0 s hook · 12,4 s riser→nhấn · 13,3 s to nhất · 20–24 s cụm SFX · 33,0 s CTA
```
Ghi dòng này vào `LOG.md` của video.
