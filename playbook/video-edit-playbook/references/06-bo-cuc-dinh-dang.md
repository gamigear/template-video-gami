# 06 · Bố cục, chữ, định dạng xuất

## 1. Khổ và tốc độ khung

- Video dọc: **1080×1920, 30 fps**. 60 fps không cần cho Reels/Shorts (nền tảng nén mạnh, chỉ tăng thời gian render).
- Bản 16:9 hoặc 1:1 (nếu cần) **phải dựng lại bố cục**, không cắt từ 9:16.

## 2. Vùng an toàn 9:16 (khung 1080×1920)

Các nguồn cho số khác nhau. Dùng bộ chặt nhất bạn chịu được, và **đo UI thật trên điện thoại** trước khi nới:

| Nguồn | Trên | Dưới (chừa) | Phải (chừa) | Ghi chú |
|---|---|---|---|---|
| FiSoft (đã dùng ~300 video Facebook Reels) | chữ quan trọng từ y 220 | 420 px (tới y 1500) | 160 px | cột like/comment bên phải, caption ở đáy |
| charlie947 `reel-export` | y 360 | 500 px (tới y 1420) | 120 px | chặt hơn ở trên và dưới |
| video-use | — | 25–30 % đáy (~480–576 px) | — | "không phải gu, là luật nền tảng" |
| Herk Edit Kit | y 200 | tới y 1600 | x 90–930 | lỏng nhất |

Phụ đề, CTA, logo, số liệu không bao giờ nằm dưới vạch đáy đã chọn.

OpenMontage dùng bộ lỏng hơn nữa cho Facebook Reels (trên 100, đáy 300, phải 60 px) — không áp, vì chưa đo UI thật.

## 3. Kích thước và khả năng đọc

- Phần tử quan trọng ≥ 100 px trên khung rộng 1080 (charlie947: chữ/số chính ≥ 120 px, nhãn ≥ 34 px); **phụ đề ≥ 50 px**.
- Vật chính chiếm 60–70 % khung.
- Khung không có phụ đề (khung 0, CTA): ≤ 5 từ trên màn hình.
- **Soi ở cỡ thật:** ảnh mỗi giây một khung ở bề rộng 360 px (phone sheet) và **200 px** (cỡ ô reel khi lướt); chữ nào không đọc được ở đó là quá nhỏ.
- Khoảng cách dọc giữa các khối xếp chồng (tiêu đề với khung/thẻ bên dưới) ≥ ~50 px; tiêu đề chạm khung bên dưới bị người duyệt chê khó đọc.

## 4. Khung 0 = thumbnail

Facebook/Instagram lấy khung đầu làm ảnh bìa khi tự phát không tiếng. Khung 0 phải là ảnh đẹp **có chữ hook** — không đen, không trống, không đang mờ vào. Đặt chữ hook hiện sẵn ở t = 0 (hoặc bắt đầu lời đọc sau ~0,35 s để khung 0 đã có chữ).

## 5. Màu và nhận diện

- **Một màu nhấn chính mỗi cảnh.** Màu nhấn sáng/chói (turquoise, cam neon…) **không làm nền toàn khung**; nền toàn khung dùng màu đậm (cobalt/navy) hoặc nền sáng trung tính.
- Đảo độ bão hoà/độ sáng mỗi lần đổi cảnh (xem `04-chuyen-dong.md` §3).
- **Test nhận diện:** chọn ngẫu nhiên 6 khung, che chữ/phụ đề — khung nào cũng phải nhận ra thương hiệu (màu, logo góc, kiểu thẻ).
- Logo/huy hiệu trên phim: tránh "viên trắng bo tròn + logo màu đầy đủ chữ" (bị chê xấu). Dấu nhỏ, đơn sắc, trong suốt nhẹ; **gửi ảnh khung mẫu cho người duyệt trước khi áp cho cả lô**.

## 6. Màn hình phần mềm trong video

- Dựng lại bằng HTML cho sắc nét (không quay màn hình mờ), có nhãn "Hình minh họa".
- File **ui-tokens** lấy mẫu màu/chữ/bo góc từ ảnh chụp phần mềm thật; mọi màn hình mô phỏng dùng chung.
- "Living Screencast": giao diện vẽ lại sắc nét, camera tự zoom theo con trỏ, con trỏ bấm/bôi/khoanh/cuộn.
- Nếu dùng ảnh chụp màn hình thật (vd chụp ChatGPT): 2/3 trên là màn hình có con trỏ thao tác, 1/3 dưới là từ khoá chữ đậm; nền sáng + lưới mờ.
- Nhịp UI chuẩn: `04-chuyen-dong.md` §4.

## 7. Font và tiếng Việt

- Web font **cục bộ** (woff2 subset `vietnamese` + `latin`), khai `@font-face` kèm `unicode-range`; không tải font từ mạng lúc render.
- **Font không tải không báo lỗi**: video ra "gần như Arial", dấu lệch. Phải có bộ kiểm ném lỗi (mẫu ở `07-hyperframes-khuon-bay.md`).
- Family/weight dùng trong CSS mà không có `@font-face` tương ứng (vd dùng weight 700 nhưng chỉ khai 400/800) → trình duyệt tự làm đậm giả; kiểm bằng readcheck.
- **Dấu chồng bị cắt:** chữ hoa có dấu chồng (Ắ, Ỗ, Ữ) cao hơn dòng thường. Với `line-height` ≈ 1,04–1,1 hoặc mặt nạ `overflow:hidden` (mask reveal), dấu bị cắt. Câu test: `ẮẰẲẴẶ ẤẦẨẪẬ ẾỀỂỄỆ ỐỒỔỖỘ ỚỜỞỠỢ ỨỪỬỮỰ` ở mọi cỡ tiêu đề; chỗ cắt thì nới `line-height` ≥ 1,15 hoặc thêm `padding-top` cho mask.
- Chuẩn hoá chuỗi NFC trước khi đưa vào HTML.
- `background-clip: text` tàng hình khi capture → dùng màu đặc + `text-shadow`.
- PIL/Canvas: luôn truyền đường dẫn font, không dùng font mặc định.

## 8. Thông số xuất (đạt chuẩn reel-export)

- H.264 High, `yuv420p`, `color_range=tv`, BT.709 (primaries/trc/colorspace), **luôn có luồng AAC** (kể cả video câm), `-movflags +faststart`.
- Lệnh: `12-lenh-ffmpeg.md` §6.

## 9. Video thật (quay màn hình, điện thoại, máy ảnh)

- Kiểm HDR: `color_transfer` ∈ {`smpte2084`, `arib-std-b67`} → tone-map về BT.709 (chỉ hạ bit-depth thì màu cháy khi nền tảng nén lại; QuickTime che giấu lỗi này).
- Hướng đọc từ `stream_side_data=rotation`, không tin tag `rotate`.
- Mọi đoạn cùng fps (`avg_frame_rate`, giữ phân số `30000/1001`) trước khi nối `-c copy`.
- Clip MP4 nằm trong composition: hiện **ảnh khung đầu** cho tới khi video chạy và **ảnh khung cuối** từ lúc video hết, để không lộ khung đen/trống.
- **Nền footage phải phủ tới hết reel**, kể cả đuôi nhạc hay thẻ kết: clip người nói hết đúng lúc hết giọng thì 0,3–0,5 s đuôi bị đen, chớp ở điểm Reels/TikTok phát lặp. Giữ khung cuối của nền bằng `tpad=stop_mode=clone:stop_duration=<giây>`, và kiểm 0,4 s cuối mọi bản render (ghost-editor, 11/2026). **Không** giữ khung cuối cho B-roll chèn giữa: ghost-editor từng làm một cảnh quán cà phê đứng hình 1,4 s; cắt ngắn đoạn chèn thay vì kéo dài.
- Lệnh: `12-lenh-ffmpeg.md` §7.

## 10. Chọn take và cắt bản quay người nói (từ ghost-editor, 11/2026)

Dùng khi có **bản quay thật người nói vào camera**, quay đi quay lại nhiều lần. Video TTS không cần phần này.

1. Ghi lời **cả bản quay**, lấy mốc từng từ. Whisper trên toàn file hay gộp câu nói lại vào một câu sạch, nên tách đoạn có tiếng bằng VAD (silero, khoảng ngừng tối thiểu 0,3 s) rồi ghi lời từng đoạn riêng. Máy M1 dùng `mlx-whisper` (`mlx-community/whisper-large-v3-turbo`).
2. Đánh số câu kịch bản; gắn mỗi đoạn với câu nó nói lại, `x` cho đoạn hỏng hoặc câu "rồi, lại nhé".
3. Mỗi câu chọn một take: đúng ý (không cần đúng chữ), trôi chảy, **ưu tiên take nói sau** vì người nói ấm dần. Nhiều câu nói một hơi thì lấy nguyên cả cụm làm một take: ít cắt hơn, giọng liền hơn.
4. Mốc cắt theo **mốc từ**, không theo mốc của cả đoạn Whisper: `a` = đầu từ đầu − 0,10…0,15 s; `b` = cuối từ cuối + 0,20…0,30 s, không quá đầu từ kế tiếp. Ngừng trong take < 0,5 s thì giữ (nhịp nói); > 1 s thì cắt.
5. Nhìn đi chỗ khác: chỉ che khi > 0,5 s hoặc đầu quay > 12°. Chớp mắt và liếc nhanh giữ nguyên. Cách che theo thứ tự rẻ trước: cắt bớt → đổi cỡ cảnh (wide/tight từ một máy 4K) → giữ đồ hoạ đang có → chèn trong khung → chèn toàn màn hình. Một reel từng che hết 31 lần liếc, khiến người nói chỉ còn trên hình 33 %.
6. Che vết cắt nhảy bằng mờ chéo 0,2 s hoặc đổi cỡ cảnh, không zoom ở mọi mốc cắt (tối đa 3 lần zoom mạnh mỗi reel).
7. Đặt chữ, thẻ và phụ đề quanh mặt: theo dõi mặt (YuNet/MediaPipe), ưu tiên dưới cằm, không đủ chỗ thì lên trên đầu, không đủ nữa thì thu nhỏ. Không đè lên mặt.
8. Mức tham chiếu (6 reel top, đo bởi ghost-editor): 113/119 chuyển cảnh là cắt thẳng; mỗi cảnh trung vị khoảng 3 s; B-roll 20–35 % thời lượng; mặt người nói ≥ 65 % thời lượng; ≤ 3 lần chèn mỗi phút.

Mã tham chiếu: kurbaitaev/ghost-editor (MIT), `references/take-selection.md`, `scripts/{vad_pauses,islands_tx,takes,plan_cut,face_track}.py`. Đã chạy thử 10/11/2026 trên clip không phải talking-head; **chưa thử bước chọn take trên bản quay thật**.
