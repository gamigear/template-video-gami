# 01 · Quy trình, điểm duyệt, cách làm việc với người duyệt

## 1. Quy trình chuẩn một video có lời đọc

```
[0] Brief + chiến lược  ─ (khuôn/hướng hình mới) trình 4–8 câu → DUYỆT
[1] Kịch bản            ─ tự kiểm (scriptcheck + checklist) → DUYỆT KỊCH BẢN
[2] Giọng đọc           ─ TTS từng câu một WAV → đo thời lượng, lặng đầu/đuôi → kiểm ASR
[3] Dựng                ─ timing lấy từ WAV thật (giọng quyết định hình, không ngược lại)
[4] Tự kiểm             ─ check + snapshot + readcheck → sửa
[5] Preview             ─ người dùng xem preview → DUYỆT PREVIEW
[6] Render + giao       ─ render → kiểm trên MP4 giao (timeline_view, LUFS) → upload
[7] Đo kết quả          ─ đường giữ chân sau khi đăng → sửa ngân hàng ý/hook
```

- **Ba điểm duyệt rẻ trước khi tốn công:** kịch bản (trước khi tạo giọng) → khung mẫu/preview (trước khi render) → bản cuối. Với phim AI thêm: duyệt khung tĩnh trước khi tốn tín dụng sinh clip.
- **Chỉ render khi người dùng đồng ý preview.** Nếu người dùng nói rõ "cứ render, bỏ bước preview" thì làm theo, ghi lại trong log.
- **Đăng lên mạng xã hội, gửi tin, upload công khai: xin phép từng bài.**

## 2. Brief và chiến lược (khi đổi khuôn hoặc hướng hình)

Trình 4–8 câu trước khi build: hình chủ đạo, nhịp, hằng số mắt bám, kiểu phụ đề, thời lượng, chuyển cảnh chính, âm thanh. Hỏi theo **tư liệu đang có**, không theo checklist cố định.

**Khi người dùng gửi video mẫu** (reel tham chiếu), mổ xẻ theo khung 5 dòng (charlie947 `reference-to-motion`) trước khi đề xuất khuôn:

1. Nhịp giữ mỗi shot (giây).
2. Cách đổi cảnh.
3. Chữ: cỡ, độ đậm, cách hiện.
4. Màu/ánh sáng (+ dòng *Look*: mã hex, font gần nhất).
5. **Một ý xuyên suốt.**

Thêm "lấy gì / không lấy gì". Tách tham chiếu **chuyển động** (video) khỏi tham chiếu **cái nhìn** (web/moodboard); chỉ lấy nhịp, bỏ logo/chữ/màu của người ta; không dùng lượt xem làm lý do.

Mổ xẻ bằng số (khi người dùng có file mẫu; không tải reel của người khác): PySceneDetect `ContentDetector` ngưỡng 27, cảnh ngắn nhất 0,5 s → độ dài cảnh (TB/min/max), số cắt/phút, nhịp lời; optical flow phân loại mỗi cảnh tĩnh / ảnh trôi / clip chuyển động; ghi hai cột "lấy cảm hứng từ" / "khác ở đâu", không đề xuất bản sao.

Lượt dò cắt rẻ hơn, không cần thư viện (hypit): `ffmpeg -vf fps=12,scale=32:32,format=rgb24 -f rawvideo -`, điểm = trung bình |chênh| ÷ 255 giữa hai khung liền nhau, ≥ 0,1 là **ứng viên** cắt (không phải nhãn biên tập), thêm sàn 0,5 s. Ghi chép thành `ANALYSIS.md` (cả bài) + `TIMELINE.md` (mỗi đoạn "giây nguồn · vai trò", ví dụ "6,07–8,27 · việc dồn lên"). Luật **giữ vai trò, làm lại hình thức**; điều người dùng không nhắc thì giữ như mẫu.

Công cụ mổ xẻ đầy đủ hơn, chạy offline (EditAtlas `video-breakdown`, Apache-2.0, chỉ cần numpy + Pillow + ffmpeg): `python3 <skill>/scripts/analyze.py reel.mp4 --out work/bd` → `breakdown.json` + ảnh `overview`/`shots_NN`/`joins_NN`/`events`. Nó đo loại mối nối (cut, dissolve, dip, flash, wipe kèm hướng, shape wipe, push, zoom, punch-in), camera (crash zoom ≥ 1,25 lần trong 0,3 s, rung ≥ 0,25 % bề ngang), timing in/giữ/ra của shot tĩnh, sự kiện chữ theo dải ngang, LUFS, tempo và cắt có theo beat không. `frames.py --at T --span 0.6 --step 0.04` lấy từng khung quanh một mối nối. `text_look.py --crop … --text "…"` đo màu chữ (gradient kèm mã hex, viền, glow, độ nghiêng) và gợi ý font Google gần giống. Clone vào thư mục riêng; chạy `python3` thường, vì `-I` bỏ qua numpy cài ở user site.

- Tác giả đo trên demo có đáp án: tìm đúng 23/24 mối nối, đúng loại 17/24; chớp sáng, nhấp nháy, phim cũ đếm thừa mối nối (14 so với 5 thật).
- Chạy thử 10/11/2026 trên reel quay màn hình CapCut (`research/reel_2054401788599994`, 25,6 s): mất 26 s, ra 22 shot. Đổi màu chữ trong ô preview nhỏ bị gán nhãn `jump cut` / `cross-dissolve` / `gradual`, nhưng đó không phải mối nối.
- → **Số chỉ là ứng viên, khung hình mới là bằng chứng**: mở `joins_NN.png` trước khi ghi tên chuyển cảnh nào; với reel tutorial quay màn hình, bỏ qua nhãn mối nối.

**Hồ sơ "khẩu vị" khi mở khuôn mới** (ghi đầu HUONG-DAN của khuôn): một câu "design read" cụ thể (không phải "hiện đại, chuyên nghiệp"); ba núm 1–10: độ đa dạng hình, cường độ chuyển động, mật độ thông tin. Phép thử: đổi tiêu đề mà video thành chủ đề khác được → còn chung chung.

## 3. Khuôn mẫu, không dựng từ đầu

Khi phải làm nhiều video cùng loại (chuỗi sản phẩm, series):

- Mỗi định dạng là **một khuôn dùng biến** (HTML/HyperFrames + file nội dung JSON). Video mới = 1 JSON + giọng + render. Không viết lại HTML cho từng video.
- Thời lượng cảnh co giãn theo độ dài giọng đọc thật (đọc từ WAV), không cố định cứng.
- Làm khuôn đầu tiên → người dùng duyệt → mới làm khuôn khác. Render theo lô khi khuôn đã duyệt.
- Chi tiết kiến trúc: `07-hyperframes-khuon-bay.md`.

## 4. Vòng tự sửa

- Sửa → render lại → chấm lại **tối đa 3 vòng**. Còn lỗi thì nêu rõ cho người dùng (lỗi gì, mốc nào, bằng chứng), không lặp vô hạn.
- Chỉ đưa preview khi tự chấm đã đạt.
- Báo cáo ghi rõ **"chỉ đo, chưa nghe"** kèm con số (LUFS, true peak, RMS theo đoạn) và mốc cần người nghe bằng tai nghe.
- **Agent phê bình tách riêng, chỉ đọc, mặc định bác bỏ:** chấm từng cảnh /10, sửa cảnh dưới 8; trả phán quyết + lỗi xếp hạng có timecode + bằng chứng + 5 việc sửa trước. Một agent mới chỉ xem khung hình rồi tóm tắt thông điệp — tóm sai là video khó hiểu.

## 5. Ghi nhận góp ý

- **Mỗi nhận xét duyệt → một luật vĩnh viễn**: một dòng trong hướng dẫn của dự án/khuôn, hoặc một kiểm tự động, hoặc sửa script. Không chỉ sửa một lần.
- Ghi chú duyệt tốt: mỗi ghi chú một việc, nói cảm giác (không cần nói cách sửa), chỉ vào mốc ("lúc 3 s"); "sửa đúng một thứ, giữ chuyển động và nhịp".
- Góp ý thẩm mỹ cho cả lô (logo, màu nền, huy hiệu): **gửi ảnh khung mẫu, chờ duyệt, rồi mới áp lô.** Bị chê thì khôi phục bản cũ, giữ bản thử trong thư mục `work/`.

## 6. Quản lý phiên bản và thành phẩm

- **Không ghi đè bản render đã giao:** làm lại thì xuất `<mã>-v2.mp4`, `<mã>-v3.mp4`, giữ bản trước để so.
- Mỗi video một thư mục `<mã>-<slug>/` chứa nội dung, audio, build, bản render, `verify/` (ảnh kiểm), `LOG.md` (điểm kiểm, cảnh yếu nhất, cách sửa lần sau).
- Một thư mục **thành phẩm** gom theo mục/khuôn bằng hard link + README; chạy lại script gom sau mỗi lần render.
- Không để bản nén tạm, ảnh snapshot, thư mục tạm lại sau khi xong việc (gitignore chúng).
- Upload Drive tự động sau render: chép MP4 vào ổ Google Drive cho máy tính theo `<thư mục gốc>/<thư mục video>/<file>.mp4`, chờ Drive xác nhận, dọn cache tự sinh; MP4 local giữ nguyên. **Tên thư mục cha trùng nhau giữa các tập** (vd `hau-ky/`) thì upload từ đường dẫn thư mục thành phẩm, không từ thư mục làm việc.

## 7. Tiết kiệm chi phí

- Tái dùng giọng đã duyệt khi đổi khuôn hình (cùng JSON + WAV → khuôn khác).
- Hook A/B: chỉ tạo lại 1 WAV.
- Thử âm thanh: trộn lại âm trên hình đã render (không render lại hình).
- Phim AI: thử rẻ bằng khung tĩnh trước khi tốn tín dụng clip; đo số lần tạo trung bình/clip trên bản thử 6–7 clip trước khi làm tập dài.
- Việc tốn tín dụng/tiền (sinh clip, ảnh trả phí, nhạc trả phí): **hỏi trước**, không tự bấm.

## 8. Tờ duyệt khung tự động trước khi render (từ ghost-editor, 11/2026)

Điểm duyệt [5] (preview) rẻ hơn nữa nếu người duyệt xem **một trang HTML** trước khi tốn công render:

- Chụp `hyperframes snapshot` ở: khung 0, 1,5 s, **ngay sau mỗi mốc cắt**, mỗi điểm nhấn lúc vừa vào và lúc đã đứng yên, khung cuối. Gom vào một trang có kèm timeline, lời theo cảnh, bảng SFX (mốc, tiếng, mức, lý do) và cảnh báo lint.
- Agent xem trang đó trước, sửa chỗ sai (chữ đè cằm, rớt dòng, thẻ chồng phụ đề), rồi mới gửi người duyệt.
- Người duyệt đồng ý thì mới render preview (720×1280, khoảng 4,5 Mbit/s, xem trên điện thoại). Đồng ý preview thì mới render bản cuối.
- Mã tham chiếu: `scripts/approval_sheet.py` của kurbaitaev/ghost-editor (MIT). Ảnh được nhúng base64 vào một file HTML khoảng 1 MB, nên gửi cho người duyệt được.
- Áp vào khuôn: có thể viết một bản nhỏ đọc danh sách cảnh trong JSON nội dung. Mốc cảnh của khuôn đã có sẵn, nên không cần phát hiện điểm cắt.
