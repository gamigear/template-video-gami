# 03 · Giọng đọc (TTS) và phụ đề

Nguyên tắc gốc: **giọng quyết định timing, không ngược lại.** Hình co giãn theo độ dài WAV thật; không ép giọng vào khung hình có sẵn, không tăng tốc giọng.

## 1. Tạo giọng

- **Mỗi câu một file WAV** (`audio/<id>.wav`, mono 48 kHz). Lợi: sửa một câu chỉ tạo lại một file; hook A/B chỉ tạo lại câu đầu; đo được từng câu.
- Câu đã có file thì bỏ qua; có cờ `--force` (tạo lại hết) và `--only 03,06` (vài câu).
- Viết **cách đọc** tách khỏi **chữ hiện**: trường `noi` cho TTS (vd "GRDP" → "gờ rờ đê pê", số → chữ), trường `doc` cho phụ đề, trường `asr` cho lời mong đợi khi kiểm. Từ nước ngoài khai số âm tiết (`am_tiet: {"FiSoft": 2}`) để chia nhịp phụ đề đúng.
- Một giọng cho cả chuỗi video. Đổi giọng giữa chừng: hỏi trước khi lồng lại video cũ (đăng xen hai giọng trên cùng kênh).

**VieNeu TTS (tiếng Việt, chạy máy, đã dùng ~300 video):**
- Server `http://127.0.0.1:23334`, `POST /synthesize {text, voice}`; liệt kê giọng `GET /voices`; trạng thái `:23336/health`.
- Giọng nhân bản tạo trong app VieNeuTTS (`~/Library/Application Support/VieNeuTTSApp/voices/voices.json`) **chỉ nạp khi server khởi động**: nếu `/voices` chưa có, chờ server rảnh (`active 0`) rồi `launchctl kickstart -k gui/$(id -u)/ai.krillin.vieneu` (~12 s).
- Tốc độ đo được: giọng nữ "Ngọc Huyền" ~0,27 s/âm tiết; giọng nam nhân bản "Tào Tháo" ~0,29 s/âm tiết (chậm hơn ~8 %).
- Các TTS khác đã loại cho tiếng Việt: `10-nguon-da-hoc.md` §4.
- **Giấy phép VieNeu:** bộ giọng v2 `vieneu/assets/voices.json` (Binh, Tuyen, Vinh, Doan, Ly, Ngoc) là CC BY-NC 4.0, không dùng thương mại; trọng số v3 Turbo + `voices_v3_turbo.json` + codec MOSS-Audio-Tokenizer-Nano là Apache 2.0. Đổi backend sang v2 hoặc gặp giọng tên trên thì kiểm lại. Đừng gọi `save_voices()` / `add_voice(save=True)`: ghi đè `voices_v3_turbo.json` trong site-packages.

## 2. Đo WAV

```
dur  = ffprobe format=duration
s0   = silence_end đầu tiên   (chỉ khi đoạn lặng đầu bắt đầu < 0,02 s)      ← silencedetect=n=-40dB:d=0.08
s1   = silence_start cuối      (chỉ khi đoạn lặng đó kéo tới hết file)
```
Lệnh: `12-lenh-ffmpeg.md` §1, §4. `[s0, s1]` là vùng có tiếng thật, dùng để chia nhịp phụ đề và tính khoảng ngừng thật.

## 3. Khoảng ngừng

Dòng thời gian: bắt đầu ở `bat_dau` (~0,35 s, để khung 0 đã có chữ hook) → mỗi câu cộng `nghi` **trước** câu rồi đặt câu, cộng cả `dur` WAV (gồm lặng của TTS) → cuối cộng `duoi` (~1,75 s).

| Chỗ | Số |
|---|---|
| `nghi` mặc định giữa câu cùng cảnh | 0,25 s |
| `nghi` câu đầu cảnh mới | 0,75 s |
| **Trước câu lộ diện** (tên sản phẩm/giải pháp) | ≥ 0,8 s, đặt tiếng nhấn vào khoảng này |
| Ngừng giữa cụm trong một câu | ≲ 0,2 s |
| Sau dấu phẩy, "Thứ nhất," | 0,2–0,4 s (giữ) |
| Hơi khi cắt lặng footage | 0,14 s thường · 0,20 s sau `.!?` · 0,24 s khi khe gốc ≥ 2 s · đệm đầu 0,22 s · đuôi 0,34 s |

- **Ngừng thật = đuôi lặng WAV trước + `nghi` + đầu lặng WAV sau.** `nghi` là lặng *cộng thêm*. In cột "ngừng thật" cho từng câu; cảnh báo khi < 0,15 s hoặc > 1,0 s (trừ trước lộ diện).
- Dấu chia cụm phụ đề (`|`) không điều khiển hơi của TTS. WAV đọc liền chỗ cần ngắt → tách thành hai câu, không chèn lặng số giữa câu.
- Cắt/nối chỉ **giữa cụm**, không trong cụm; chỉ cắt sau khi từ tắt hẳn (transcript kết thúc từ sớm 40–80 ms so với lúc phụ âm tắt); không fade từ cuối.
- Video không nhạc: khe giữa câu là **room tone** lấy từ WAV, không phải lặng số (`05-am-thanh-sfx.md` §5).
- **Cân loudness từng câu**: đo LUFS mỗi WAV, chênh > 1,5 LU thì cân gain trước khi mix; chỉ hạn đỉnh, không kéo từng câu về đỉnh riêng.

## 4. Kiểm giọng bằng ASR

- faster-whisper `large-v3-turbo` (CPU int8 chạy được trên M1), `language="vi"` (không dùng model `.en`; base/small nghe tiếng Việt kém), `beam_size=5`, `vad_filter=False`, `initial_prompt` = danh sách tên riêng.
- Resample 16 kHz, **đệm 0,6 s lặng hai đầu**; bỏ segment ảo ở phần đệm cuối (`no_speech_prob > 0,5`).
- Chuẩn hoá trước khi so: NFC, chữ thường, số 0–10 → chữ, chỉ giữ chữ/số. `difflib.SequenceMatcher.ratio() ≥ 0,92` là đạt.
- **Tên thương hiệu luôn nghe bằng tai**: ASR nghe "FiSoft" thành "FaceSoft"/"GigiSoft" khá thường xuyên; với clip AI tự nói thì ngược lại, model cũng hay đọc sai tên.
- Mốc từ ước lượng (chia đều âm tiết) có thể lệch: bật `word_timestamps=True`, so onset thật với mốc ước lượng ở các từ dùng làm neo hình, báo lệch > 0,15 s.
- **In từ chèn thêm/thay thế** (đoạn `insert`/`replace` mức từ của difflib) cho mọi câu, kể cả câu đạt: một từ thừa (TTS đọc "…" thành "chấm", "/" thành "xuyệt", "%") chỉ hạ ratio vài phần trăm nên lọt ngưỡng 0,92. Đã làm ở FiSoft ngày 02/11/2026, in `+chèn ~thay -thiếu`. Bỏ qua chỗ chỉ khác khoảng trắng ("Fi Soft" = "FiSoft"). Nếu chèn hoặc thay ra tên dấu câu (chấm, phẩy, gạch, xuyệt, ngoặc, dấu) mà kịch bản không có, câu nhận nhãn `DẤU` và tính là lệch. Chỉ xét những từ được chèn nên "chấm công" trong kịch bản không bị báo nhầm. Ca đối chứng: bỏ một chữ khỏi kịch bản trong khi WAV vẫn đọc chữ đó.
- ASR chép đúng một từ bị cắt cụt là chuyện thường → kiểm "từ nguyên vẹn" phải nhìn dạng sóng/strip tại mốc cắt.

## 5. Phụ đề

**Dữ liệu:** chia câu thành cụm theo `|`; thời gian mỗi từ chia đều trong `[s0, s1]` theo trọng số âm tiết (từ có dấu phẩy cuối +1,2 đơn vị nghỉ) → `groups[{start, end, words[{text, start, end}]}]`, xuất `captions.json` để công cụ kiểm dùng lại.

Mốc từ đo thật (nếu ước chia đều lệch > 0,15 s ở nhiều chỗ): lấy `word_timestamps` của faster-whisper trên từng WAV câu rồi khớp với kịch bản bằng quy hoạch động kiểu hypit: nhóm tối đa 4×4 từ, phạt bỏ sót 0,5, chèn 0,35, thay = khoảng cách sửa chữ ÷ độ dài × độ tin; từ không khớp chia khe giữa hai láng giềng theo số chữ; kẹp trong `[s0, s1]`; mốc đầu làm tròn xuống khung, mốc cuối làm tròn lên. TTS đọc đúng kịch bản nên căn ép (wav2vec2 CTC) còn chính xác hơn, nhưng cần torch. Đo lệch trên 2 video trước khi đổi.

Đã đo (FiSoft 02/11/2026, 2 reel, 230 từ): ước chia đều lệch whisper trung vị 0,07 s, nhưng 19–20 % từ lệch > 0,15 s, dồn hết vào **từ ngay sau dấu chấm/hỏi giữa một câu** (ước sớm 0,15–0,32 s), vì luật chỉ cộng nghỉ sau dấu phẩy. Đầu câu (s0) đúng tuyệt đối. Sửa không cần ASR (FiSoft `_tools/chia-tu.mjs`, đã áp 13 khuôn): lấy các khoảng lặng trong câu mà silencedetect đã dò để đo s0/s1, ghép các dấu câu với các khoảng lặng **cả câu một lượt bằng quy hoạch động giữ thứ tự** (tổng |tâm lặng − mốc ước| nhỏ nhất, mỗi cặp ≤ 0,6 s, bỏ một dấu tốn 0,6, bỏ một lặng không tốn), từ trước dấu kết thúc ở đầu lặng, từ sau dấu bắt đầu ở cuối lặng, trong mỗi đoạn vẫn chia theo âm tiết; dấu không neo được thì nghỉ 1,2 âm tiết → trên 14 reel 13 khuôn, từ lệch whisper > 0,15 s 172 → 104. Hai bẫy: (1) **lặng khép âm tắc** — chỗ khép /k/ /t/ /p/ dài ~0,1 s cũng qua silencedetect −40 dB/0,08 s, còn chỗ ngừng ngắn ở dấu phẩy có khi chỉ xuống −35 dB nên không được dò; neo vào đó làm từ sau sớm 0,36 s → khoảng lặng < 0,12 s không làm neo; (2) **ghép tham lam** từng dấu theo thứ tự để dấu trước giành lặng của dấu sau → dùng quy hoạch động. Chỗ TTS ngừng mà kịch bản không có dấu câu vẫn lệch (tới 0,7 s); bỏ thời gian lặng khỏi phép chia thì hoà (lợi 2 khuôn, hại 3), nên sửa bằng cách thêm dấu phẩy vào lời ở đó. whisper `word_timestamps` không dùng làm chuẩn được: lượng tử 20 ms và hay đặt từ sau khoảng ngừng sớm; mốc chắc chắn là lúc hết lặng.

**Luật cụm:**

| Luật | Số |
|---|---|
| Sàn mỗi cụm | ≥ 0,35 s (ngắn hơn hiện như chớp → gộp) |
| Trần mỗi cụm | ≤ 6 từ, ≤ 2,2 s, ≤ 8 âm tiết (vượt → tách) |
| Hiện | sớm 2 khung (~0,08 s) trước từ đầu; opacity 0,1 s, y 12→0 trong 0,25 s `power3.out` |
| Tô từ (karaoke) | đổi màu ở `w.start − 0,04` trong 0,1 s |
| Tắt | `nextShow = next.start − lead` (lead là thời gian hiện sớm, 0,08 s; Băng chuyền 0,14 s); `hide = max(show + 0,05, min(end + 0,4, nextShow − thời_gian_tắt))`. Hai cụm **không bao giờ mờ chéo**: cụm trước tắt hẳn rồi cụm sau mới hiện. Công thức cũ (`next.start − 0,08` khi khoảng trống < 0,45 s, ngược lại `end + 0,4`) để hai cụm chồng 2–4 khung ở mỗi chỗ nối, và vẫn chồng khi khoảng trống 0,45–0,6 s. Đã sửa ở 12 khuôn FiSoft ngày 02/11/2026. |
| Hiện phủ trọn lời | hypit bắt buộc lúc hiện ⊇ lúc đọc (nối kiểu `cut`: cụm cũ giữ tới hết lời, cụm mới không hiện trước lúc cụm cũ tắt; lead/tail chỉ nới phần hiện). Công thức "Tắt" ở trên, khi hai cụm liền nhau trong một câu (khe 0), làm cụm cũ tắt hẳn **sớm 0,08 s** trước khi đọc xong từ cuối (đo 02/11/2026: 11/24 và 8/23 chỗ nối trên 2 reel). Thấy từ cuối bị nuốt thì ở khe < lead + tắt: đổi cụm ngay lúc hết lời bằng `tl.set`, hoặc giảm lead còn 0,04 s. |
| Tắt hẳn | sau fade thêm `tl.set(group, {opacity: 0, visibility: "hidden"}, end)`; tự kiểm: tua tới `end + 0,01` mà còn thấy → lỗi |

**Hình:**
- Phụ đề ≥ 50 px trên khung 1080; nằm trên vạch đáy vùng an toàn (`06-bo-cuc-dinh-dang.md` §2).
- Một kiểu phụ đề cho cả video. **Không bao giờ chữ sáng trên nền sáng**: đo tương phản pixel phía sau từng cụm trên bản render (WCAG AA), không nhìn mắt — nhất là phụ đề không nền đè lên ảnh/khung màn hình.
- Hộp phụ đề `overflow: visible`; không dùng `left: 50%; translateX(-50%)` cho hộp phụ đề (căn bằng flex/`text-align`).
- Tiếng Việt đơn âm: chia 1–3 từ/cụm như tiếng Anh là quá vụn; chia theo cụm nghĩa 4–6 từ.
- Clip AI có thoại thật: phụ đề theo **lời thật trong clip**, không theo kịch bản; có nhãn tên vai, mỗi vai một màu.
- Khung không có phụ đề (khung 0, CTA): ≤ 5 từ trên màn hình.

## 6. Neo hình vào lời

- Mốc hình lấy từ cụm chữ trong lời (`luc: "ba bước"`): tìm cụm (NFC, chữ thường, bỏ dấu câu) trong danh sách từ của chính cảnh, lần đầu; không thấy → build dừng (không đoán).
- Mốc = từ.start − cảnh.start + `OFF` (−0,06 s).
- **Điểm nhấn "chạm đất" đúng từ**: bắt đầu tween sớm `min(thời lượng tween, 0,5 s)` để khung kết của hiệu ứng trùng lúc đọc từ. Bảng `LAND` trong build phải khớp duration tween trong HTML; đổi một bên thì đổi bên kia.
- Dung sai hình so với từ neo: từ 0,2 s sau tới 1,8 s trước; khuyến nghị dẫn trước 0,5 s. Hai mốc cách nhau < 1,3 s → dời mốc về đầu câu.
- Không bật hai phần tử độc lập cùng lúc (một thứ, ngừng, thứ kế). Tổng thời lượng hình chèn ≥ lời đọc + 1 s, giữ khung cuối ≥ 1 s.
