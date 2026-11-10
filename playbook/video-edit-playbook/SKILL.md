---
name: video-edit-playbook
description: Sổ tay dựng/edit video đúc kết từ ~300 reel và ~23 phim AI đã làm thật (FiSoft, 10/2026) — dùng cho MỌI repo có việc làm video. Tra khi viết kịch bản video ngắn, tạo giọng đọc TTS tiếng Việt, làm phụ đề, dựng bằng HyperFrames/GSAP/three.js, chèn SFX và nhạc, trộn âm và chuẩn loudness, xuất file cho Reels/Shorts/TikTok, hậu kỳ clip AI (Google Flow/Veo/Omni), kiểm tra chất lượng trước khi giao, hoặc tra lệnh ffmpeg. Keywords: video editing, short-form vertical video, reels, shorts, motion graphics, voiceover, subtitles/captions, sound design, SFX, loudness LUFS, ffmpeg recipes, AI video post-production, HyperFrames, GSAP, Remotion alternative, QA checklist.
---

# Sổ tay dựng video (video-edit-playbook)

Kinh nghiệm **đã kiểm chứng trên sản phẩm thật**, không phải lý thuyết: mỗi luật ở đây đến từ một lỗi đã gặp, một góp ý của người duyệt, hoặc một con số đo được. Đọc file này trước; mở file trong `references/` khi cần chi tiết.

## 1. Thứ tự ưu tiên khi các nguồn nói khác nhau

1. Lời người dùng trong phiên + `CLAUDE.md` của repo đang làm.
2. Hợp đồng render của công cụ (skill `hyperframes`, `hyperframes-core`…) — luật tất định của nó là bắt buộc.
3. **Sổ tay này.**
4. Skill bên thứ ba (threejs-skills, gsap-skills…) — chỉ để tra API; gợi ý trái với luật video (vd `setAnimationLoop`) thì bỏ.

## 2. Chọn quy trình

| Việc | Quy trình | Đọc |
|---|---|---|
| Video ngắn có lời đọc (reel sản phẩm, giải thích, chuỗi nhiều video) | brief → kịch bản → TTS từng câu → khuôn HyperFrames dùng biến → kiểm → preview → render → kiểm file giao → upload | 01, 02, 03, 04, 05, 06, 07, 08 |
| Phim ngắn nhân vật bằng AI | kịch bản 7 clip × 10 s → kinh thánh nhân vật → khung đầu/cuối → (hỏi tín dụng) → sinh clip → kiểm clip → cắt/che/thay màn → dựng chữ → mix → đóng dấu | 09, 05, 08, 12 |
| Footage quay thật / quay màn hình | kiểm HDR, xoay, fps → chuẩn hoá → cắt theo transcript, cắt giữa cụm, afade 30 ms → room tone | 06 §9, 12 §7, 03 §3 |
| Bản quay người nói vào camera (nhiều lần nói lại) | ghi lời từng đoạn VAD → chọn take theo mốc từ → mốc clip theo lưới khung → chữ quanh mặt → tờ duyệt khung | 06 §10, 07 §9, 01 §8 |
| Video cắt theo beat nhạc | lưới beat theo dải kick, kiểm pha | 05 §7, skill `music-to-video` |
| Chỉ cần lệnh ffmpeg | | 12 |

## 3. Luật cứng (không vi phạm khi chưa hỏi người dùng)

**Duyệt và vận hành**
1. Ba điểm duyệt rẻ trước khi tốn công: **kịch bản** (trước TTS) → **preview / khung mẫu** (trước render) → bản cuối. Phim AI: duyệt khung tĩnh trước khi sinh clip. Khi xin render bản cuối hoặc theo lô, hỏi luôn **máy render**: M1 hay mbp2016 (`11` §7).
2. **Đăng, gửi, upload công khai: xin phép từng lần. Tiêu tín dụng/tiền (sinh clip, ảnh, nhạc trả phí): hỏi trước.**
3. Không ghi đè bản đã giao: làm lại xuất `-v2`, `-v3`; bản cũ cất `work/`, không xoá.
4. Tối đa **3 vòng** tự sửa → render → kiểm; còn lỗi thì báo rõ (lỗi, mốc, bằng chứng).
5. **Mỗi góp ý của người duyệt → một luật vĩnh viễn** (dòng trong CLAUDE.md/HUONG-DAN, một kiểm tự động, hoặc sửa script). Góp ý thẩm mỹ cho cả lô: gửi ảnh mẫu, chờ duyệt, rồi mới áp lô.

**Nội dung**
6. Chỉ nói cái có thật; số chỉ lấy từ danh sách được phép; màn hình dựng lại có nhãn "Hình minh họa"; nội dung AI bật nhãn AI.
7. Khung 0 là ảnh có chữ hook (thumbnail khi tự phát không tiếng). Tắt tiếng vẫn hiểu.

**Giọng, nhịp, hình**
8. **Giọng quyết định timing.** Mỗi câu một WAV; đo thời lượng và vùng có tiếng; không tăng tốc giọng; cảnh co giãn theo WAV.
9. Chuỗi nhiều video cùng dạng = **một khuôn dùng biến + JSON nội dung**, không viết lại HTML từng video.
10. Render **tất định**: một timeline đã pause; không `Math.random`/`Date.now`/rAF/`setAnimationLoop` làm nguồn thời gian; tài nguyên cục bộ; ghim phiên bản công cụ.
11. Mỗi lúc một chuyển động chính; chỉ tween `transform`/`opacity`; một quyền opacity mỗi phần tử; mọi tween xong trước mốc cắt.
12. Điểm nhấn **chạm đất đúng từ** (bắt đầu sớm bằng thời lượng tween, ≤ 0,5 s).
13. Không khung nào đứng yên > 2,2 s mà không ghi lý do; > 3 s là lỗi.
14. Vùng an toàn 9:16 (chữ từ y ≥ 220, chừa đáy ≥ 420 px, phải ≥ 160 px); phụ đề ≥ 50 px; phần tử chính ≥ 100 px.
15. Font cục bộ + **bộ kiểm font ném lỗi** (font hỏng không báo gì); chuỗi NFC; thử chữ hoa có dấu chồng.
16. Phụ đề: cụm 0,35–2,2 s, ≤ 6 từ; hiện sớm 2 khung; cụm trước tắt hẳn rồi cụm sau mới hiện; không chữ sáng trên nền sáng.

**Âm thanh**
17. SFX gắn vào hành động thấy được; trần ≈ **1 SFX / 2,2 s**; tiếng căng **≤ 1 / 7 s**; đặt theo **đỉnh/attack đo được**, không theo đầu file.
18. Hook = impact trầm + một tiếng cao sáng (~2,5 kHz). Lặng 0,5–2 s trước lộ diện, rồi tiếng nhấn to nhất. Ramp nhạc ra trước CTA.
19. Ưu tiên giọng > SFX > nhạc. Master: `alimiter=limit=0.891:level=disabled` → loudnorm **2 lượt** → **−14 LUFS, TP ≤ −1 dBTP**.
20. ffmpeg trộn nhiều nhánh: mỗi nhánh `adelay=…,asetpts=N/SR/TB,atrim=0:DUR,apad=whole_dur=DUR`, `amix=normalize=0:duration=first`, `-t DUR`, `-nostdin` (không thì treo). **Thiếu `asetpts` sau `adelay` thì `atrim` có thể cắt mất đoạn lặng chèn trước, kéo câu về 0 s** (gặp khi trước đó có `loudnorm`). Biến shell trong filtergraph luôn viết `${DUR}` (zsh hiểu sai `$DUR[c0]`, `$OFF:linear`).
21. Chỉ dùng SFX/nhạc có giấy phép rõ; cấm tiếng meme và file Epidemic/Storyblocks chưa mua; ghi nguồn từng file.

**Kiểm**
22. **Đo trên file giao, không tin code.** Báo cáo ghi "chỉ đo, chưa nghe" + 5 mốc cho người nghe bằng tai nghe; không bao giờ viết "nghe ổn".
23. Mỗi kiểm tự động mới phải có **ca cố ý sai** chứng minh nó bắt được lỗi.

**Phim AI và 3D**
24. Clip AI lặp câu → **cắt hẳn cả hình lẫn tiếng**; phụ đề theo lời thật trong clip; mọi cú phóng neo quanh watermark.
25. Không dùng công cụ vượt chống bot/reCAPTCHA, xoay vòng tài khoản, hay lái web app bằng cookie xuất ra.
26. three.js: thời gian chỉ từ timeline (`mixer.setTime(t)`), `setPixelRatio(1)`, `preserveDrawingBuffer: true`; sửa mã dùng chung thì so khung trước/sau.
27. Không cài skill bắt in quảng cáo hoặc gọi dịch vụ trả phí ngầm; mượn ý chỉ lấy tên, con số, cách kiểm.

**Footage quay thật** (thêm 10/11/2026, từ ghost-editor)
28. Mốc clip footage = số khung / fps **cắt bớt** ở 6 chữ số (`0.066666`, không `0.067`); cắt hình và tiếng ở cùng mốc đã đưa về lưới khung (07 §9).
29. Nền footage phủ tới hết reel (giữ khung cuối cho đuôi nhạc); kiểm 0,4 s cuối không đen (06 §9).

## 4. Bảng số tra nhanh

| Mục | Số |
|---|---|
| Khổ | 1080×1920, 30 fps (clip AI 720×1280 @24 → phóng lanczos) |
| Thời lượng reel lời đọc | 30–45 s; 100–120 âm tiết cho 32–38 s |
| Tốc độ đọc tiếng Việt | 3,3–3,9 âm tiết/s (0,27–0,29 s/âm tiết) |
| Câu | ≤ 20 âm tiết; hook ≤ 14 âm tiết |
| Lộ diện tên sản phẩm | 35–45 % thời lượng (chặn ngoài 30–50 %); `nghi` trước ≥ 0,8 s |
| Khoảng ngừng | giữa cụm ≲ 0,2 s · sau phẩy 0,2–0,4 s · giữa câu 0,25 s · đầu cảnh 0,75 s · ngừng thật 0,15–1,0 s |
| Nhịp đầu/đuôi | lời bắt đầu 0,35 s · đuôi 1,75 s |
| Ease | vào `0.16,1,0.3,1` · ra `0.6,0,0.9,0.35` (≈ ½ thời gian vào) · chuyển `0.65,0,0.35,1` |
| Stagger | ≥ 0,09 s; thẻ 0,2–0,25 s |
| Giữ để đọc | ≥ max(1,5 s, ký tự/15 + 1,5 s); CTA ≥ 2 s (an toàn 3 s) |
| Phụ đề | 0,35–2,2 s, ≤ 6 từ / 8 âm tiết, ≥ 50 px; hiện sớm 0,08 s |
| SFX | ≤ 1/2,2 s; căng ≤ 1/7 s; master SFX −4 dB; pop −10…−16, whoosh −9…−12, riser −16, sting −11, impact hook −16 (+ hook-cao +1) |
| SFX so với đỉnh giọng p95 (đo trên bản chỉ SFX, chưa A/B) | UI −14 · whoosh −12 · impact −8 dB (05 §11) |
| Cắt take (bản quay thật) | `a` = từ đầu − 0,10…0,15 s · `b` = từ cuối + 0,20…0,30 s · giữ ngừng < 0,5 s · che liếc > 0,5 s hoặc > 12° |
| Nhạc | −11 dB + sidechain ratio 6 (reel) · −29…−30 LUFS/đoạn, ratio 5 (phim có thoại) |
| Loudness giao | −14 LUFS, TP ≤ −1 dBTP (khuôn đặt −1,5); cân từng câu chênh ≤ 1,5 LU; CTA không thấp hơn lời > 3 dB |
| Xuất | H.264 High, yuv420p, tv, bt709, AAC 192k 48 kHz, `+faststart` |
| ASR đạt | difflib ratio ≥ 0,92 |
| Clip AI | 7 × 10 s + end card 3 s; 40–46 chữ/10 s; tông sáng TB ~165/255 |

## 5. Chỉ mục `references/`

| File | Nội dung |
|---|---|
| `01-quy-trinh-va-duyet.md` | quy trình 7 bước, điểm duyệt, brief, mổ xẻ video mẫu, vòng tự sửa, agent phê bình, phiên bản, tiết kiệm, tờ duyệt khung tự động (§8) |
| `02-kich-ban-va-hook.md` | luật nội dung, 10 nguyên tắc giữ chân, cổng 3 giây, vòng mở, mẫu cấu trúc, tốc độ đọc, checklist |
| `03-giong-doc-phu-de.md` | TTS từng câu (VieNeu), đo WAV, khoảng ngừng, ASR, phụ đề karaoke, neo hình vào lời |
| `04-chuyen-dong.md` | bảng số chuyển động, CustomEase, nhịp, chuyển cảnh, nhịp UI, công thức hiệu ứng, plugin GSAP, cấm, chống "vẻ AI" |
| `05-am-thanh-sfx.md` | đường cong năng lượng, trần SFX, ánh xạ hành động → tiếng, canh đỉnh/attack, mức trộn, master, beat, kiểm, giấy phép, đo SFX so với giọng (§11) |
| `06-bo-cuc-dinh-dang.md` | khổ, vùng an toàn, cỡ chữ, khung 0, màu, màn hình mô phỏng, font tiếng Việt, xuất, video thật, chọn take bản quay người nói (§10) |
| `07-hyperframes-khuon-bay.md` | kiến trúc khuôn dùng biến, hợp đồng tất định, âm trong khuôn, bộ kiểm font, three.js, **bảng ~40 bẫy**, kho ý tưởng 13 khuôn, CLI, mốc clip theo lưới khung (§9) |
| `08-kiem-tra-qa.md` | thứ tự kiểm, ngưỡng, kiểm hình/âm, agent phê bình, luật cho công cụ kiểm, mẫu báo cáo |
| `09-phim-ai-hau-ky.md` | phim AI end-to-end: prompt Flow/Omni, bộ lọc nội dung, kiểm clip, bảng lỗi clip, cắt/che/thay màn xanh, mix, chèn video giải pháp |
| `10-nguon-da-hoc.md` | ~40 repo/công cụ đã xem: giấy phép, dùng/bỏ, lý do — tra trước khi nghiên cứu nguồn mới |
| `11-trien-khai-tham-chieu.md` | đường dẫn mã đã chạy thật (khuôn, công cụ kiểm, hậu kỳ), phụ thuộc, cách mang sang repo mới |
| `12-lenh-ffmpeg.md` | sổ lệnh: ffprobe, trích khung/strip, trộn âm, đo âm, cắt/nối/che, xuất, HDR/xoay/fps, bẫy, tách đồ hoạ thành mẫu CapCut (§9) |

## 6. Cập nhật sổ tay

Sổ tay này dùng chung cho mọi repo. Khi một dự án video học được điều mới (góp ý người duyệt, bẫy mới, con số đo được, nguồn mới):

1. Ghi vào **file `references/` đúng chủ đề**, ngắn, có con số và lý do; nguồn mới vào `10`. Giữ nguyên số mục `§` đang có (các file trỏ chéo nhau theo số mục), thêm mục mới ở cuối.
2. Trái với luật cũ → sửa luật cũ, ghi ngắn vì sao đổi; không để hai luật mâu thuẫn.
3. Luật đủ quan trọng để vi phạm là hỏng sản phẩm → thêm vào §3; con số hay tra → §4.
4. Chỉ ghi điều dùng lại được ở dự án khác; chi tiết riêng dự án để trong `CLAUDE.md` của repo đó.
5. Không dán log dài, không chép mã có giấy phép không rõ.
