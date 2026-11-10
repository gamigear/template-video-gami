# Nghiên cứu reel "Motion video": đèn rọi làm lộ chữ (Rj Design)

_Ngày: 2026-11-10 · Nguồn: <https://www.facebook.com/reel/1031124079924311/> (link chia sẻ `share/v/14t4VadzQ7w`)_

## 1. Thông tin chung

| Mục | Giá trị |
|---|---|
| Trang | Rj Design – Studio créatif (Madagascar), handle `@jerry-rjdesign` |
| Đăng | 2026-09-02 · tiêu đề trang ghi 176K lượt xem, 2,8K cảm xúc |
| Mô tả | "Motion video #MotionDesign #RjDesign #AnimationGraphique #BrandVideo #Madagascar" |
| Kỹ thuật | 11,14 s · 1920×1080 **ngang 16:9** · 25 fps · AV1 + AAC 48 kHz stereo |
| Âm lượng | −26,1 LUFS tích hợp (nhỏ), LRA 13,9 LU, true peak −0,4 dBTP |
| Cắt cảnh | **0 cú cắt**: một cảnh liền, mọi chuyển cảnh do chuyển động tạo ra |

File: `src/video.mp4`, `src/video.info.json`; khung hình `pv/` (480 px, đủ 278 khung), lưới `sheets/s1–s3.jpg`
(mỗi ô cách 0,12 s), khung gốc `full/`, sóng âm `full/wave.png`, phổ `full/spec.png`.

## 2. Ý tưởng một câu

Trên nền đen, một chiếc **đèn rọi tối giản** tự lắp ráp rồi bật sáng. Chùm sáng hình tam giác **quét qua lại như rọi sân khấu**.
Mỗi lần dừng, nó làm lộ một dịch vụ của studio, rồi đến logo. Cuối cùng là màn trắng có handle.
Đây là video **giới thiệu dịch vụ / showreel nhận diện**, không có lời và không có cảnh quay thật.

## 3. Storyboard theo thời gian

| Thời điểm | Hình | Âm thanh |
|---|---|---|
| 0,00–0,55 | Đen hoàn toàn | Cụm tiếng "tách/pop" 0,2–0,5 s (−7 dB) |
| 0,60–1,30 | **Thân đèn** (chữ nhật bo góc, phát sáng) bay lên từ dưới, lắc lư, xoay nghiêng như đang tìm chỗ | Tiếng động nhỏ 0,8–1,3 s |
| 1,40–2,30 | **Chóp/kính đèn** (nửa vòm) rơi xuống, nảy vài lần, khớp vào thân | Tiếng lách cách nhẹ 1,3–1,9 s |
| 2,30–2,90 | **Bật đèn**: chùm tam giác hắt thẳng lên trên, mép có glow | Đòn mạnh nhất (2,31 s, −6 dB), vệt cao tần ở phổ 2,2–2,5 s = tiếng "bật công tắc + lấp lánh" |
| 2,90–3,90 | Đèn xoay xuống phải, chùm quét ngang, lộ **"Brand / *Design*"** góc dưới phải | Tiếng ù/riser kéo dài 2,3–4,4 s (đoạn to nhất) |
| 4,00–4,90 | Quét sang trái: **"Motion / *Design*"** góc dưới trái | Whoosh 4,4 s |
| 5,00–6,10 | Đèn bay lên dưới trái, chùm hắt lên phải: **"Montage / *Video*"** góc trên phải | Cặp whoosh 4,9–5,4 s |
| 6,20–7,10 | Đèn ở phải, chùm hắt lên trái: **"Logo / *Animation*"** góc trên trái | Cặp whoosh 6,1–6,4 s |
| 7,20–8,00 | Đèn ở trái giữa, chùm mở rộng nhất: **logo "RJ Design."** | Cặp whoosh 7,2–7,4 s |
| 8,00–8,90 | Chùm tắt dần, đèn trượt ra mép phải, chỉ còn chấm sáng | Whoosh 8,6–8,8 s |
| 8,90–9,40 | **Mảng trắng** đẩy từ phải sang trái, có motion blur, che kín khung. Handle **"@jerry-rjdesign"** trượt vào, mờ rồi nét | Nhỏ dần (−33 dB) |
| 9,40–10,60 | Giữ màn trắng, handle ở giữa (~1,2 s) | Gần như im |
| 10,60–11,14 | Handle thoát từng chữ sang phải, có blur | 7–8 tiếng "tick" nhỏ đều nhau ở phổ 10,6–11 s, ăn khớp từng chữ biến mất |

**Nhịp:** 5 "trạm" chữ, mỗi trạm giữ 0,8–1,1 s và chuyển trong 0,2–0,3 s. Ai cũng đọc kịp 2 từ/trạm.
Phần mở đầu (lắp đèn) chiếm **2,3 s ≈ 20 % thời lượng**. Đó là "hook" tò mò: người xem chưa biết vật thể sáng là gì.

## 4. Cách dựng (đảo ngược kỹ thuật)

1. **Đèn = 2 shape layer** (thân: chữ nhật bo góc; kính: nửa vòm), tô trắng, thêm Glow để có quầng sáng.
   Hai phần được animate riêng, có overshoot/bounce, rồi parent vào nhau sau khi khớp.
2. **Chùm sáng = mặt nạ tam giác** có đỉnh tại kính đèn, xoay quanh đỉnh đó (anchor point = vị trí kính).
   Mép chùm có glow trắng mềm ~20–30 px.
3. **Nội dung bên dưới là cố định.** Có một lớp nền sáng (#DEE0E6, những khối cầu 3D mờ xám-tím nhạt #D1D1DB) và chữ.
   Chùm sáng dùng làm **track matte (alpha)** cho lớp này. Vì vậy chữ chỉ hiện trong vùng chùm sáng chạm tới.
   Ở khung 7,8 s còn thấy bóng mờ "Logo Animation" lọt ngoài vùng sáng. Điều này cho thấy mỗi cụm chữ còn có
   fade in/out riêng, chứ không chỉ dựa vào mask.
4. **Mỗi trạm = đèn đổi vị trí + xoay**, và chữ đặt ở góc đối diện đèn. Bố cục xoay vòng qua đủ 4 góc:
   dưới phải → dưới trái → trên phải → trên trái → giữa (logo). Mắt người xem phải di chuyển, nên không bị nhàm.
5. **Kết:** tấm trắng đẩy ngang có directional blur (chuyển cảnh kiểu push), handle vào/ra bằng hiệu ứng
   chữ có motion blur theo từng ký tự.

Phần mềm gốc nhiều khả năng là After Effects (shape + track matte + Glow + Directional Blur).

## 5. Hệ thiết kế

| Thành phần | Chi tiết đo được |
|---|---|
| Bảng màu | Đen #000 · trắng #FFF · nền chùm sáng #DEE0E6 / #D1D1DB · nhấn **đỏ đô #A8283A** · chữ #0A0A0A |
| Chữ dòng 1 | Sans đậm, hình học (gần Inter/Helvetica Bold), đen |
| Chữ dòng 2 | **Serif nghiêng** (gần Lora/Source Serif Italic), đỏ đô, thụt lề so với dòng 1 |
| Logo / handle | Sans hình học tròn (gần Poppins SemiBold/Regular) |
| Ánh sáng | Một nguồn duy nhất; mọi thứ ngoài chùm đều đen tuyệt đối, nên độ tương phản rất cao |

Công thức đối lập **sans đậm + serif nghiêng màu nhấn** giúp mỗi cặp 2 từ trông như một logo nhỏ.

## 6. Vì sao hiệu quả

- **Ẩn dụ "spotlight" = "làm nổi bật thương hiệu"** khớp đúng nội dung (studio thương hiệu đang rọi đèn vào dịch vụ của mình).
- **Hook không cần chữ**: 2 giây đầu là vật thể bí ẩn tự lắp ráp, có tính cách (lắc lư, nảy), nên người xem tò mò ở lại.
- **Tối giản tuyệt đối**: một vật thể, một hành động lặp lại 5 lần, mỗi lần đổi góc. Dễ đọc kể cả khi tắt tiếng.
- **SFX khớp từng chuyển động**: mỗi cú quét có whoosh, chữ thoát có tick. Không dùng nhạc nền, nên âm thanh "sạch", cảm giác cao cấp.
- Ngắn (11 s), loop được (kết trắng → mở đen tạo độ tương phản khi lặp).

**Điểm yếu nếu đem dùng cho Reels:**

- Khung **ngang 16:9**: xem trên Reels/TikTok sẽ có viền hoặc bị crop.
- Âm lượng −26 LUFS, nhỏ hơn mức chuẩn mạng xã hội (~−14) khoảng 12 dB.
- Màn handle trắng giữ 1,2 s hơi dài so với phần còn lại.

## 7. Áp dụng cho dự án của mình

**Dựng lại bằng HyperFrames (phù hợp nhất):**

- Chùm sáng: `clip-path: polygon(...)` trên lớp nền + chữ, xoay quanh đỉnh. Hoặc dùng SVG `<mask>` có polygon và
  `filter: blur` cho mép.
- Glow: `filter: drop-shadow` / `box-shadow` trắng nhiều lớp. Đèn là 2 `div` bo góc, chạy GSAP `back.out` / `bounce.out`.
- Mỗi trạm là 1 tween timeline (đèn `x, y, rotation` + chùm `rotation` + chữ `autoAlpha`), dài 0,25 s, ease `power3.inOut`.
- Bản dọc 9:16 cho Reels: đổi các góc thành trên/dưới. Chữ đặt cách mép an toàn, đèn quét theo trục dọc.
- SFX: whoosh ngắn mỗi lần quét, một "switch-on" + riser lúc bật đèn, tick khi chữ thoát. Chuẩn về −14 LUFS.

**Dựng bằng CapCut:**

CapCut không có mask tam giác và không có track matte. Cách xoay xở là dựng sẵn chùm sáng thành video có alpha (từ HyperFrames/AE)
rồi đè lên. Hoặc chấp nhận dùng mask hình chữ nhật xoay. Kết quả kém mượt hơn bản gốc.

**Biến thể nội dung đề xuất:** đổi 4 dịch vụ thành 4 lợi ích sản phẩm / 4 tính năng app / 4 khoá học, giữ nguyên trò "đèn tự lắp + rọi".
Bối cảnh "đèn pin trong bóng tối" cũng hợp với chủ đề game kinh dị/khám phá (Minigame).
