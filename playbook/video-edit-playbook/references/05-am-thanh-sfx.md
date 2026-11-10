# 05 · Âm thanh: SFX, nhạc, loudness

Mục tiêu: "đã tai, đã mắt" để giữ chân, nhưng **không lạm dụng gây nhàm**. Câu chủ đạo (Barty-Bart `sound-effects`): *Claude không nghe được, nên mọi thứ phải đo; giao vài mốc rủi ro nhất cho người nghe bằng tai nghe; không bao giờ báo "nghe ổn".*

## 1. Đường cong năng lượng

- **Mạnh nhất ở 1,5 s đầu** (hook): impact trầm + chuyển cảnh lớn, **chồng thêm một tiếng cao, sáng** (clang kim loại ~2,5 kHz) ở 0,05 s → một trầm + một cao, không phải hai tiếng cùng dải. Tai người tò mò với tần số cao (bài học reel Quạ HD, A/B đã được người dùng chọn).
- **Giữa:** nhịp vừa, pop/click/whoosh nhỏ theo từng beat.
- **Trước lộ diện:** cao trào dày nhất → **lặng 0,5–2 s** → tiếng nhấn **to nhất** của video. Cao trào không trùng tiếng to nhất.
- **CTA:** bùng lại (impact + sting logo); kết có thể nối vòng về đầu.

## 2. Trần số lượng

| Loại | Trần |
|---|---|
| SFX nhỏ (pop/click/whoosh) | ≈ 1 SFX / 2,2 s (video 35 s ≤ 15). ~8 tiếng/18 s nghe "có chủ ý", ~20 nghe "stock" |
| Tiếng căng (alert, sting chói, drone, tiếng cao gắt) | **≤ 1 / 7 s**, đếm riêng ngoài trần trên. Đoạn kể khổ hay dồn alert: đếm trước khi build |
| Chuyển cảnh lớn | 1 mỗi lần đổi cảnh, không lặp cùng file hai lần liền |

Trần ở trên dành cho reel **có lời đọc**: 1 tiếng / 2,2 s ≈ 4,5 tiếng / 10 s. Bảng nhịp theo loại phim của EditAtlas `sound-design` (số đo của Clipwing real-sfx trên 9 reel SFX đã hoàn thiện, **chưa A/B trên khuôn FiSoft**):

| Loại phim | Tiếng / 10 s | Khe dài nhất |
|---|---|---|
| Chỉ có SFX (không lời, không nhạc) | 7–15, trung vị ~11; khe trung vị ~0,7 s | ~2,5 s, báo lỗi khi > 3 s; có tiếng trong 2 s đầu |
| Có nhạc riêng | 3–12 | ≤ 5 s |
| Giọng dẫn | 1,5–8 (một talking-head được duyệt bằng tai: 2,6) | ≤ 8 s |

- Các tiếng cách nhau < 80 ms tính là một cử chỉ (một mốc nhiều lớp). Mốc lớn tối đa 3 lớp (hit + đuôi whoosh + mảnh vụn), không thay bằng một file thật to.
- Hit nặng chiếm ≤ ~1/3 số cử chỉ. Một file không dùng quá 2 lần: dùng các take đánh số của cùng họ tiếng. Tiếng UI giữ một họ cho cả phim.
- Vật thật trên hình (ly, đá, giấy) dùng foley thật, không dùng pop UI (pop trên vật thật nghe như hoạt hình).
- Bed ambience cho phim **chỉ SFX**: một tiếng nền tối, đều, ở trung vị **−54 dBFS**. Nghe thử: −56…−50 "vừa", ≥ −44 "quá to", không có bed thì "trống". Không bao giờ đặt bed dưới giọng hay nhạc.

## 3. Gắn tiếng vào hành động trên hình (không rải ngẫu nhiên)

| Trên hình | Tiếng |
|---|---|
| Chuyển cảnh, vật bay | whoosh / swoosh / slide |
| Chữ, thẻ bật ra | pop |
| Con trỏ bấm | click (Nhật: 決定ボタンを押す) |
| Nhập liệu | gõ phím (cắt/lặp đúng thời lượng gõ, fade 50 ms) |
| Dấu tích, thành công | ting / ding / success |
| Hook, CTA | impact / boom (+ tiếng cao ở hook) |
| Ngay trước lộ diện sản phẩm | riser ngắn |
| Lỗi | glitch nhẹ |
| Hover | tick |
| Nền | ambience rất thấp |
| Máy quay 3D bay, khối dựng lên | swoosh/approach; tap/knock, clang nhẹ |

SFX sinh ra để "lừa" tai cho hợp nhịp, không cần giống âm thật ngoài đời. **Không tổng hợp tiếng bằng sóng sin/oscillator** (Tone.js…): dùng file thật.

## 4. Canh thời điểm

- **Đặt tiếng nhấn vào khoảng ngừng trước câu nói tên**, không đặt dưới lời đọc (phần hạ nhạc khi có giọng nuốt mất).
- **Đặt theo đỉnh/attack đo được, không theo đầu file.** Cắt bỏ lặng/room tone đầu file. Định nghĩa attack = mẫu đầu tiên vượt (đỉnh − 30 dB); đặt file sớm `attack` giây trước khung chạm (chính xác hơn "đỉnh" với SFX có phần build dài).
- Đo thật trên một bộ SFX (10/2026): đỉnh `whoosh` ở +0,161 s sau đầu file (nghe từ +0,092 s), `pop` +0,119 s, `swipe` +0,326 s, `impact` +0,361 s, `sting` +0,025 s → nếu đặt `adelay = t` theo đầu file thì pop trễ 3–4 khung, whoosh trễ ~5 khung. Cần bảng bù: `t − đỉnh` cho pop/click/ting, `t − đỉnh + 2 khung` cho whoosh.
- whoosh **sớm 2 khung** so với chuyển động; pop/click **đúng khung**; riser kết thúc ngay trước khoảng lặng lộ diện (không "kết đúng tiếng nhấn" nếu đã có luật lặng trước lộ diện).
- Mã đo đỉnh/attack (cần numpy):
  ```python
  import subprocess, numpy as np
  def dinh_attack(path, sr=48000, db=-30):
      raw = subprocess.run(["ffmpeg","-v","error","-i",path,"-ac","1","-ar",str(sr),"-f","f32le","-"],
                           capture_output=True, check=True).stdout
      x = np.abs(np.frombuffer(raw, np.float32)); pk = x.max()
      return x.argmax()/sr, int(np.argmax(x >= pk*10**(db/20)))/sr   # (giây tới đỉnh, giây tới attack)
  ```

## 5. Mức trộn

Ưu tiên: **giọng > SFX > nhạc**. Giọng luôn rõ nhất; SFX không át giọng.

| Lớp | Mức (so với impact 0 dB) |
|---|---|
| impact | 0 dB, SFX to nhất |
| whoosh / cắt cảnh | −4 |
| pop / click / tick / riser | −6 |
| gõ phím | −8 |
| tiếng cao ở hook | thấp hơn impact 3–6 dB (dải 2–6 kHz nghe to hơn mức đo được); đo thực tế thấp hơn giọng ~2 dB |
| nhạc nền | −12 dB dưới SFX; dưới lời thấp hơn mức chỉ-nhạc 12–15 dB (sidechain/ducking) |

Một bộ khuôn đã duyệt dùng: master SFX −4 dB, pop −10…−16, whoosh −9…−12, riser −16, sting −11; nhạc −11 dB + sidechain ratio 6.

- **SFX nghe quá nhỏ → nâng chính file SFX**, không tăng volume cue: cộng một âm −38 dB vào nền −17 dB gần như không đổi gì.
- **Nhạc:** chỉ dùng khi có file có bản quyền; nếu không thì để trống (người dùng thêm nhạc trên nền tảng). **Ramp nhạc ra trước sting/CTA**, đừng để đuôi nhạc tự tắt dưới CTA. Nhạc sinh máy mặc định "hype" → đưa hai bed trái ngược cho người dùng nghe.
- **Video không nhạc:** khe giữa hai câu phải là **room tone** lấy từ WAV (4–8 khung, fade 10 ms, cross-fade đồng công suất 40 ms vào đuôi tắt), không phải lặng số `anullsrc` (nghe như "nối máy").
- **Cân từng câu giọng về cùng loudness**, chỉ hạn đỉnh (kéo một câu về đỉnh riêng làm câu đó nhỏ hơn ~5 dB). Đo LUFS từng WAV; chênh > 1,5 LU thì cân gain trước khi mix.
- Chuỗi xử lý giọng TTS (OpenMontage, **chưa A/B**): lọc thấp 80 Hz, cắt ~500 Hz, +2–3 dB ở 2–5 kHz, hạ nhẹ 6–8 kHz, nén 3:1 (attack 1–5 ms, release 10–20 ms). Chỉ áp khi người dùng nghe A/B thấy khác.
- Cắt clip có tiếng: `afade` 30 ms hai đầu mỗi đoạn; chỉ cắt sau khi từ đã tắt hẳn (transcript kết thúc từ sớm 40–80 ms so với lúc phụ âm tắt).

## 6. Master và đích loudness

- Chuỗi: mix PCM → `alimiter=limit=0.891:level=disabled` (≈ −1 dBFS; **thiếu `level=disabled` thì file tự to lên**) → `loudnorm` **hai lượt** một lần duy nhất ở cuối.
- Đích cho Reels/Shorts: **−14 LUFS tích hợp, true peak ≤ −1 dBTP** (khuôn FiSoft đặt −1,5). Phương án an toàn hơn cho loa điện thoại/nén AAC: −16 LUFS, TP < −4 (Barty-Bart) — chưa thử, đừng đổi nếu chưa A/B.
- Đo trên **file stereo giao**; đo thêm bản **mono** (mono đọc thấp hơn ~3 dB, và có thể lộ triệt pha). Báo khi TP > −1 dBTP.
- HyperFrames có thể encode lại audio nhỏ hơn master → remux WAV master vào bản render rồi đo lại LUFS trên file giao (lệnh ở `12-lenh-ffmpeg.md`).
- Bảng RMS theo đoạn chức năng (hook / thân / lộ diện / CTA): **CTA thấp hơn đoạn lời > 3 dB = lỗi**; SFX to hơn lời = lỗi.

## 7. Nhạc có beat

- Tìm drop bằng năng lượng theo dải tần; **kiểm lại lưới beat tự động** (hay lệch 2 beat hoặc nhầm gấp đôi/nửa tempo, hay bám hi-hat lệch nhịp).
- Lưới beat theo **dải kick**: lowpass 120 Hz tìm kick, dời cả lưới theo trung vị; đo lại sau khi nối nhạc (pha trong ±25 ms); ghi BPM **đo được**, không ghi BPM đặt hàng. Dời điểm bắt đầu nhạc để cắt cảnh rơi đúng beat, báo lệch từng cắt (ms).
- `npx hyperframes beats` cho lưới nhanh, nhưng đối chiếu với pha kick.

## 8. Kiểm trên file MP4 giao (không tin code)

1. LUFS tích hợp, true peak (stereo + mono).
2. Chỗ to nhất có rơi vào cảnh lộ diện/CTA không; có khoảng lặng trước nó không.
3. Mỗi SFX đã thêm **thật sự nghe được**: đo RMS/dải tần cửa sổ quanh cue so với nền (vd hook-cao: dải 2–8 kHz ở 0,05–0,35 s phải nhảy rõ, như −59 → −26 dB).
4. Bảng RMS theo cảnh.
5. Báo cáo ghi rõ "chỉ đo, chưa nghe" + **5 mốc giao người nghe bằng tai nghe**: hook, riser → sting, tiếng to nhất, cụm SFX dày nhất, CTA.
6. **Sync đo thật** (EditAtlas `sound-design` `check.py`): trên bản render chỉ có SFX (§11), tìm lại từng tiếng bằng tương quan chéo với dạng sóng file gốc của nó. Lấy vị trí thật trừ mốc khung dự định; **lệch > 1 khung (33 ms ở 30 fps) là lỗi cue**. Cách này kiểm được cả bảng bù đỉnh/attack ở §4 sau khi đã render. Thêm vào cùng lượt: số cử chỉ / 10 s và khe dài nhất (bảng §2), file lặp > 2 lần, mono fold-down. Ghép các mốc cần nghe thành một `listen.wav` để giao người nghe.

Khi thử thay tiếng: trộn lại âm trên hình cũ (không render lại hình) thành bản A (đối chứng trộn lại) / B / C, đo cùng bảng, đưa người dùng nghe chọn. Bản A phải khớp âm đã giao trước khi tin so sánh (FiSoft 11/2026: −29 dB, mức nhiễu AAC). **Bẫy:** HyperFrames/Chrome đưa giọng mono ra stereo ở mức nguyên vẹn, còn `aformat=channel_layouts=stereo` của ffmpeg hạ −3 dB mỗi kênh → giọng trong bản trộn lại nhỏ hơn 3 dB, A lệch còn −17 dB; dùng `pan=stereo|c0=c0|c1=c0` cho giọng mono.

## 9. Nguồn tiếng và giấy phép

- **Một bộ SFX chung cho cả chuỗi** để giữ nhận diện. Hỏi người dùng nguồn trước khi lấy.
- **Được phép:** Mister Horse Free (dùng thương mại; giấy phép 1 người, cấm phát tán lại → **tự tải bằng tài khoản của mình**, không dùng bản người khác chép lên Drive), 効果音ラボ soundeffect-lab.info (miễn phí thương mại, cấm phát tán lại; rất hợp UI: con trỏ, nút xác nhận, hiện tiêu đề), thư viện HeyGen qua `/media-use resolve --type sfx|bgm`, Kenney/Freesound **CC0** (phân phối lại được), Mixkit Free (không phân phối lại).
- **Cấm:** tiếng meme (game, phim, Windows, Mario, Minecraft…), file Epidemic `ES_…` / Storyblocks `…-SBA-…` khi chưa có gói, gói "Anime SFX" không rõ nguồn (chỉ nghe tham khảo chất tiếng rồi tìm bản có giấy phép), thư viện **EditAtlas/sfx** (không có giấy phép, không ghi nguồn từng file; xem `10-nguon-da-hoc.md` §3).
- Ghi nguồn mỗi file vào manifest/`CREDITS.txt`; nhạc không rõ nguồn → ghi "LICENCE NOT CONFIRMED", không dùng.
- Mỗi file trong bộ: đo thời lượng, attack, đỉnh, RMS, tần số trọng tâm, tỉ lệ năng lượng > 2 kHz; đặt tên theo chức năng (`hook-cao`, `pop`, `chon`, `chuyen-canh`, `lo-dien`, `cang`…); đỉnh ≤ −1 dBFS; cắt lặng đầu file.

## 10. Lệnh trộn

Đồ thị ffmpeg mẫu (đặt cue, sidechain, vá treo `amix`) và lệnh đo: xem `12-lenh-ffmpeg.md` §3–§4 và `07-hyperframes-khuon-bay.md` §3.

## 11. Đo SFX so với giọng trên một bản tách riêng SFX (từ ghost-editor, 11/2026)

Bảng §5 đặt mức SFX so với impact. Phần này **thêm một bước đo**, không thay bảng §5.

- Đo đỉnh giọng (p95 của đỉnh từng khối, dBFS) trên WAV giọng đã cân. Render thêm một bản **chỉ có SFX** (tắt giọng và nhạc), rồi đo đỉnh từng tiếng và so với đỉnh giọng.
- Mức đích của ghost-editor (đỉnh SFX so với p95 đỉnh giọng): UI/pop −14 dB, whoosh −12, impact −8, meme −3. To hơn giọng là lỗi; không nghe được cũng là lỗi.
- Lợi ích: mức SFX bám theo **giọng thật của từng video** (VieNeu, giọng nam/nữ khác nhau), không theo số gõ tay. Sửa bằng cách đổi gain của file SFX (§5), không tăng âm lượng bản mix cuối.
- Lần chạy thử (10/11/2026, clip Douyin có nhạc nền): whoosh đo được −8,6 dB, impact −5,2 dB so với giọng, cao hơn đích khoảng 3 dB nhưng vẫn qua ngưỡng QA của tool.
- Trạng thái: **chưa A/B trên khuôn FiSoft hay Đào Lửa**. Muốn áp thì đo 3 reel đã duyệt trước, so với các mức này rồi mới chốt ngưỡng.
