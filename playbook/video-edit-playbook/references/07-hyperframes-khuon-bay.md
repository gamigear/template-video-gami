# 07 · HyperFrames: khuôn dùng biến, âm thanh trong khuôn, three.js, bảng bẫy

Đọc cùng các skill `hyperframes*` (hợp đồng render chính thức). Phần này là kinh nghiệm từ 13 khuôn đã render ~300 reel (HyperFrames 0.8.159, GSAP 3.15, three r186, M1 Pro). Bản triển khai: `11-trien-khai-tham-chieu.md`.

## 1. Kiến trúc "khuôn dùng biến"

```
content/<mã>.json ─► voice (TTS từng câu) ─► build (đo WAV → mốc → sinh HTML + trộn âm) ─► check/preview ─► render (+ loudnorm 2 lượt + upload) ─► kiểm
```

**JSON nội dung:** mỗi cảnh có `loi[]` gồm câu `{id, doc, nghi?, noi?, asr?}`; trường hình trỏ vào lời bằng `luc` (cụm chữ có trong lời). Trường gốc: `giong`, `am_tiet`, `to_mau`, `nhip: {bat_dau: 0.35, duoi: 1.75}`, `cta`. Chi tiết giọng, nhịp, phụ đề: `03-giong-doc-phu-de.md`.

**Dòng thời gian cảnh:**
- Câu: `t = bat_dau`; mỗi câu `t += nghi; start = t; t += dur_wav`. `TOTAL = t + duoi`.
- Cảnh: `start = câu đầu.start − lead` (0–1,0 s); `dur = cảnh sau.start + overlap (0,35–0,55) − start`; cảnh cuối kéo tới `TOTAL`; cảnh mờ ra từ `dur − 0,4`.
- Mốc hình: `A(key, phrase)` → từ.start − cảnh.start − 0,06; điểm nhấn trừ thêm thời lượng tween (`LAND`).

**Sinh thư mục video:**
- Chép `compositions/ assets/ hyperframes.json`, ghi `package.json` (`npx --yes hyperframes@<phiên bản cố định> preview/check/render`). **Ghim phiên bản** HyperFrames: công cụ kiểm dùng hàm nội bộ.
- `index.html`: mỗi cảnh một `div.clip` với `data-composition-src`, `data-variable-values='{"<key>": …}'`, `data-start`, `data-duration`, `data-track-index`; lớp nền chạy suốt (track 0); phụ đề `data-track-kind="captions"`; `<audio id="vo-<id>">` từng câu xen kẽ hai track; `bgm-ducked.wav` và `sfx-stem.wav` mỗi thứ một track. **Mọi media có `id`.**
- Cảnh đọc biến: `(window.__hfVariablesByComp||{})[id] || window.__hyperframes.getVariables()`. Cờ `--defaults` ghi dữ liệu làm `default` để mở khuôn trong Studio.
- Đầu ra để soát: `captions.json`, `build/cues.json` (`{dur, voice[], cues[{t, sfx, gain, trim?, note}]}`), `build/timeline.txt` (CẢNH / GIỌNG / MỐC HÌNH / SFX / PHỤ ĐỀ / CẢNH BÁO).
- Build tự cảnh báo: chữ quá số ký tự, một mục hiện < 1,3–2,5 s, logo bắt đầu trước đầu cảnh, cụm phụ đề ngoài sàn/trần, câu cấm.

**Render:** `npx --yes hyperframes@x render -o raw.mp4 --fps 30 -q delivery` → loudnorm 2 lượt (`-c:v copy`) → `ebur128` in LUFS → upload. Nhiều JSON một lệnh = render lô. Cờ hậu tố `-v2` báo lỗi nếu file đã có. Thời gian (M1 Pro): reel 2D 35 s ≈ 1–2 phút; reel three.js 35 s ≈ 2 phút 15 giây.

**Khuôn mới:** chép từ khuôn đã ổn định nhất (gồm `mix-audio.py` đã vá treo), không viết lại từ đầu. Làm một bản thử → người dùng duyệt → mới render lô.

## 2. Hợp đồng render tất định (luật cứng)

- Một timeline GSAP **đã pause** cho mỗi composition, đăng ký vào `window.__timelines[id]`; renderer tua theo từng khung.
- Không `Math.random` (dùng `hash(n)` theo t: `s = sin(n*127.1+311.7)*43758.5453; s - floor(s)`), không `Date.now`, không `setInterval`/rAF làm nguồn thời gian.
- Tài nguyên cục bộ (GSAP, font, three) — không CDN lúc render.
- **Tua tất định:** tua tới, tua lui, nhảy thẳng tới mốc ra cùng một khung. Khi sửa khuôn, chụp cùng mốc theo 3 thứ tự (tăng, giảm, ngẫu nhiên) phải giống từng byte.
- Thuộc tính bị nhiều tween tác động suốt video (lớp flash chung, đổi class) **kẹt khi tua ngược** → tính trong driver theo khung: `tl.fromTo(drv, {t: 0}, {t: END, ease: "none", onUpdate: () => draw(drv.t)})`.
- Timeline con ngắn hơn `data-duration` → composition bị ẩn → **khung đen chớp cuối cảnh**. Kết mỗi timeline bằng neo `tl.to({}, {duration: SLOT}, 0)`; chẩn đoán: so `__timelines[k].duration()` với `data-duration`.
- Mốc kết thúc tween làm tròn theo bội `1/fps`; ease đuôi dốc (`expo.in`, `power4.in`) răng cưa ở ranh giới dưới khung.
- Mọi tween trong cảnh kết thúc **trước** mốc cắt (thời điểm xong muộn nhất = start + delay lớn nhất của stagger + duration).

## 3. Âm thanh trong khuôn

Ba lớp: giọng (`<audio>` từng câu), `sfx-stem.wav`, `bgm-ducked.wav`. Đồ thị ffmpeg đầy đủ: `12-lenh-ffmpeg.md` §3.

- **Stem SFX** từ `cues.json`: mỗi cue `[trim + fade 0,15 s] → aformat 48 kHz stereo → volume (gain + master −4 dB) → adelay → asetpts=N/SR/TB → atrim=0:DUR → apad=whole_dur=DUR`, rồi `amix=normalize=0:duration=first`, `-t DUR`.
  - **Vá treo:** đồ thị `amix=duration=longest,apad,atrim` treo ngẫu nhiên ở cuối file (ffmpeg 9, CPU 95 %, không bao giờ xong). Bắt buộc `asetpts=N/SR/TB,atrim=0:DUR,apad=whole_dur=DUR` sau `adelay` trên **từng nhánh** + `duration=first` + `-t DUR` + `-nostdin`.
- **Sidechain:** gộp các câu giọng (cùng hàm mix) thành `voice-sidechain.wav`, dùng làm khoá hạ nhạc (`ratio=6:attack=40:release=450`, nhạc −11 dB).
- **Lọc SFX theo trần** (khuôn có nhiều thao tác UI): xếp theo ưu tiên (0 = hook, đổi thẻ, logo, CTA) rồi thời gian; tiếng cách tiếng đã giữ < 0,5 s thì bỏ (trừ `hook-cao`, `riser`); trần `floor(TOTAL/2,2) + 1`; vượt trần thì bỏ ưu tiên 2, rồi ưu tiên 1 có gain thấp nhất.
- Mức từng SFX của bộ khuôn đã duyệt: `05-am-thanh-sfx.md` §5.
- **Khoảng trống đã biết (11/2026):** stem SFX của các khuôn reel đặt cue theo **đầu file**, chưa trừ đỉnh/attack, và master chưa qua `alimiter`; hai thứ này mới có trong mix phim AI (`09-phim-ai-hau-ky.md` §6). Khuôn mới nên làm đúng ngay: `adelay = t − attack`, `alimiter=…:level=disabled` trước loudnorm.
- HyperFrames có thể encode lại audio nhỏ hơn master → remux WAV master rồi đo lại trên file giao.

## 4. Bộ kiểm font (chèn vào `index.html` sinh ra)

Font không tải **không báo lỗi**: video ra "gần như Arial", dấu tiếng Việt lệch, render vẫn xanh.

```js
// build quét mọi @font-face trong brand.css → SPECS = ["normal 800 60px \"Be Vietnam Pro\"", ...]
(async () => {
  for (const spec of SPECS) {
    const faces = await document.fonts.load(spec, "Việt Nam đẹp ưỡn ẹo 0123 FiSoft").catch(() => []);
    if (!faces.length || faces.some(f => f.status !== "loaded")) {
      window.__hfStartupError = "FONT CHƯA TẢI: " + spec;
      throw new Error(window.__hfStartupError);
    }
  }
})();
```
Không dùng `document.fonts.check()` làm điều kiện (sub-composition chèn lại CSS nên check trả đúng/sai không ổn định). Weight dùng trong CSS phải có `@font-face` tương ứng (không thì trình duyệt làm đậm giả). Chữ vẽ lên canvas: chờ `fontsReady()` trước khi vẽ.

## 5. three.js trong video

Skill `threejs-*` viết cho web thời gian thực; khi gợi ý khác luật dưới thì **luật dưới thắng** (khớp `hyperframes-animation` → adapter three):

- **Thời gian chỉ từ timeline:** vẽ trong `draw(t)` gọi từ tween đại diện `tl.to(P, {t: dur, duration: dur, ease: "none", onUpdate: () => draw(P.t)}, 0)`. Cấm làm nguồn thời gian: `renderer.setAnimationLoop`, `requestAnimationFrame`, `THREE.Clock`/`Timer`, nút `time` của TSL, `mixer.update(delta)`. Clip glTF: `mixer.setTime(t)`.
- Đóng gói three bằng esbuild từ `src/` → `assets/three-*.js` (**tên file phải chứa "three"**, không thì lint báo `missing_three_script`). Dựng async → `window.__hf.buildReady["<id>"] = build().then(s => { S = s; S.renderAt(pend); })`.
- Renderer: khung 1080×1920, `setPixelRatio(1)`, `preserveDrawingBuffer: true`, bóng `PCFShadowMap` (`PCFSoftShadowMap` bỏ từ r182). Không OrbitControls/raycast/sự kiện chuột. Chưa dùng WebGPU/TSL.
- Tween HTML phủ trên canvas: `fromTo(..., {immediateRender: false}, at)`.
- Nhãn HTML bám vật 3D: đo kích thước **một lần** lúc dựng, cập nhật vị trí trong `onUpdate` (đo trong callback → `check` cảnh báo `gsap_callback_dom_measurement`).
- Texture canvas động (màn laptop): vẽ lại mỗi khung theo t, bỏ qua khi bị che (nắp < 12°). Tấm hai mặt: vẽ lại mặt sắp lộ **đúng lúc bắt đầu lật** (khi còn quay lưng) để tua tới lui vẫn đúng.
- Khung 9:16 hẹp: camera lùi theo độ trải ngang của cảnh; sương mù co giãn theo khoảng cách camera (nhìn xa không tối). Mỗi bước một `POSE` + trôi ngang tuyến tính để không khung nào đứng yên.
- Chữ chính để HTML phía trên canvas (dễ đọc, readcheck kiểm được — readcheck không đọc được chữ trong WebGL).
- **Sửa `src/` xong thì so khung trước/sau:** bundle → chép vào bản sao một video đã render → `npx --yes hyperframes@0.8.159 snapshot <dir> --frames 8 --no-end --no-browser-gpu --describe false` → so điểm ảnh với gói cũ. Sửa dọn mã phải ra 0 khác biệt.
- Gỡ lỗi nhanh không cần HyperFrames: `python3 -m http.server` + trang dev gọi `seek(t)` trong console.

## 6. Bảng bẫy (triệu chứng → cách sửa)

| Triệu chứng | Nguyên nhân → cách sửa |
|---|---|
| Bản render mất tiếng một cue (preview có) | `<audio>` không có `id` → mọi media có `id` |
| Cả video trắng xoá | lớp phủ `mix-blend-mode` blend với nền trong suốt → bỏ blend, dùng opacity/gradient |
| Hiệu ứng lộ ở khung 0 trước cue | `fromTo` áp "from" ngay lúc dựng → ẩn bằng CSS hoặc `set` tại cue; `immediateRender: false` |
| Khung đầu rack focus/nhòe giật | tween `filter` từ `none` → khai `filter: blur(0px)` trong CSS |
| Chuyển động rung | hai tween cùng thuộc tính một phần tử → gộp, hoặc tách hai node (ngoài scale, trong xoay/dịch) |
| Hai tween cùng opacity nhấp nháy ~10 Hz | **một quyền opacity cho mỗi phần tử** mỗi cửa sổ thời gian |
| Cảnh trắng/đen ngay trước khi cắt | `data-duration` root ≠ clip con, hoặc timeline con ngắn hơn → cùng một nguồn số + neo `tl.to({}, {duration: SLOT}, 0)` |
| Hai nhãn chồng vài khung | chữ cũ ra và chữ mới vào trùng giờ → cũ ra xong rồi mới vào |
| Con trỏ lệch nút khi camera zoom | con trỏ ngoài node camera → đặt trong node camera, gốc zoom đúng vào nút |
| Đo vị trí sai | `getBoundingClientRect` dưới cha đang scale → đo một lần sau `document.fonts.ready`, trước mọi tween `immediateRender`, không đo trong `onUpdate` |
| Chữ mờ khi zoom | `will-change` trên phần tử camera → bỏ |
| Lint báo lỗi tween `letterSpacing`; layout giật | chỉ tween `transform`/`opacity`; muốn chấm → ô thì vẽ ô ở kích thước cuối rồi scale |
| Chữ gradient biến mất khi render | `background-clip: text` tàng hình khi capture → màu đặc + `text-shadow` |
| Video trong composition không chạy/nhảy | `<video data-start>` nằm trong `.clip` có thời gian → đặt trong wrapper không thời gian; video `muted`, âm trộn riêng |
| Video trong composition treo/đứng hình khi render | khoảng keyframe > 5 s → mã hoá lại clip trước khi đưa vào: `-g 30 -keyint_min 30 -sc_threshold 0` (OpenMontage) |
| Render nhiều video nền chậm/treo | từ 5 video nền trở lên → `render --workers 1` (OpenMontage) |
| Clip độ phân giải thấp ra hộp nhỏ giữa nền đen | scale-cover + crop, không fit + pad |
| Lộ khung đen khi video tải/kết sớm | bọc ảnh khung đầu (trước khi chạy) và khung cuối (`-sseof -0.25 … -update 1`, `12-lenh-ffmpeg.md` §2) |
| Cảnh thoát bị cảnh mới đè sai lớp | chuyển cảnh "thu nhỏ vào màn hình" cần `z-index` cho cảnh đang thoát |
| Chấm tròn lộ ra trước khi nét SVG vẽ | tự ẩn bằng dasharray + `linecap: round` vẫn vẽ đầu nét → DrawSVGPlugin `"0%"→"100%"`, rút về `"100% 100%"` rồi `autoAlpha: 0` |
| Font rơi về hệ thống, render vẫn xanh | bộ kiểm font §4 |
| Màn app trong điện thoại trống khi render | đổi màn bằng `xPercent`, không bật/tắt opacity |
| `check` báo `text_not_painted` cho chữ viền rỗng | tô ruột chữ bằng màu nền đục + viền |
| `check` báo tương phản ở phụ đề | hai cụm mờ chéo → cụm trước tắt hẳn rồi cụm sau hiện |
| `check --frame-check` báo `content_overlap` ở `#cap-…` (2–4 khung mỗi chỗ nối) | công thức tắt cụm phụ đề cũ → dùng công thức ở 03 §5. `check` lấy mẫu thưa nên **có thể sót** (Băng chuyền chồng 3 khung mà báo 0) → xác nhận bằng `snapshot --at` ở các mốc chỗ nối −0,2…0 s |
| Tiêu đề dài gãy dòng | tự thu cỡ theo số ký tự có sàn: `min(base, 880/(0.72·ký_tự))`, sàn 56 px; câu hỏi ≤ ~16 ký tự/dòng, ≤ 2 dòng |
| Thu cỡ chữ đo sai | chỉ đo sau khi font tải, bên trong `buildReady` |
| Điểm nhấn lệch lời sau khi đổi duration tween | sửa bảng `LAND` trong build cùng lúc với HTML |
| Thẻ/logo lọt ra trước đầu cảnh | tăng `nghi` trước câu hoặc `lead` cảnh 0,7 → 1,0 s |
| Build dừng sau khi sửa lời | `luc` phải còn trong lời; hai bước < 1,3 s thì dời `luc` về đầu câu |
| Khung 0 trống | vẽ sẵn ~55 % hình chính ở khung 0 (thumbnail) |
| Nút trong ảnh dọc dài không thấy | ảnh 2:3 chỉ thấy ~69 % trên → `cuon` trước `bam`; thao tác cách nhau ≥ 0,5 s |
| Nhãn 3D đè tiêu đề/phụ đề/nhau | kẹp x 70–920; điểm gắn cao hơn y≈560 lật nhãn xuống; trong dải phụ đề (y > 1270) thì ẩn; hai nhãn chồng → nhấc một nhãn + kéo dài chân |
| Khối 3D dưới che chữ khối trên | 4–5 khối: giảm tiến về camera, hạ thấp, nghiêng ít, lắc nửa biên độ; cách đỉnh phụ đề ≥ 45 px |
| Màu nhấn cam không đủ tương phản 3:1 trên nền sáng | tối màu lại (vd #FF7A45 → #E2602C) |
| Còn chuyển động lúc cắt cảnh | mọi tween dừng trước khi cảnh thoát |
| Sửa code mà video không đổi | kiểm trên MP4 vừa render (trích khung tại mốc), không tin mã nguồn |
| Build treo ở bước ghép âm | §3 vá treo `amix` |
| Cảnh báo `check` bỏ qua được | `canvas_content_at_edge` (canvas phủ khung là chủ ý); `clip_media_fit` của nhạc lệch 0,1 s |

## 7. Kho ý tưởng hình (13 khuôn, dùng lại được)

| Khuôn | Ý tưởng + kỹ thuật |
|---|---|
| Băng chuyền | HUD có thanh tiến độ suốt video; danh sách bước dọc tô sáng theo tiến độ, bước qua có ✓; "nhiễu" = 2 bản sao lệch màu 0,35 s chỉ ở 3 điểm nhấn |
| Chữ động 3 điểm | không cần màn hình; cụm chữ khổng lồ 3 lớp lệch rồi khớp; mỗi điểm một tấm nền màu, số khổng lồ đập đúng lúc đọc "Một/Hai/Ba"; cảnh mở thu nhỏ vào số "1" (match cut) |
| Contentta | nền giấy có đốm/hạt trôi; sans hẹp + 1–3 từ serif nghiêng nhấn; thẻ băng dính; khung màn hình có mũi tên vẽ tay + zoom; số lớn khoanh tròn "chạm đất"; phụ đề karaoke không nền |
| Demo tương tác | điện thoại 4 loại màn (lưới chọn, biểu mẫu gõ + bấm + ✓, danh sách trượt, biểu đồ không số); đổi màn bằng `xPercent` |
| Hành trình hồ sơ | một thẻ đi qua 3–5 trạm, trạng thái đổi theo trạm; điểm rời rạc nối về khối trung tâm; cảnh mở thu nhỏ vào thẻ |
| Lướt màn hình | giả quay màn hình trên ảnh chụp: con trỏ SVG di/bấm (scale 0,82 + gợn 0,3→1,6)/bôi (`scaleX`)/khoanh/zoom/cuộn; camera `{s,x,y}` `transform-origin 0 0` kẹp không lộ mép; 1/3 dưới là từ khoá; 3 kiểu đổi thẻ xoay vòng |
| Màn hình máy tính | cửa sổ desktop menu trái, bấm menu → màn chức năng trượt lên; 5 loại màn; dữ liệu che bằng •• |
| Sa bàn 3D | thế giới three.js, chuỗi cú máy `inOut` ≤ 1,1 s rồi trôi chậm; nhãn HTML bám vật; cảnh 2D phóng + mờ để "lao xuyên" vào 3D; phong cách cắm được (`theme`, `spots`, `cams`, `update(t)`, `render()` tilt-shift) |
| Sơ đồ giải pháp | dây rối nét đứt MorphSVG duỗi thành nan về hub (`expo.inOut` 0,75 s, xám → màu nhấn); chấm dữ liệu chạy MotionPath bám đầu nét DrawSVG; thoát bằng mống mắt (iris); lau chéo |
| Thiết bị 3D | laptop three.js, màn là canvas texture; nắp gập/mở làm nhịp kể (gập = bài toán, mở = lộ diện) |
| Chữ khối 3D | chữ có độ dày, lật −180° lộ mặt sau, rơi thành đống, gom lại; camera quỹ đạo chậm, cuối lao vào tấm |
| Trước/Sau | màn chia đôi; vạch chia gạt đúng lúc đọc "sau"; cảnh mở ép thành vạch chia (match cut) |
| Mẫu 3D dự trữ | thẻ bay chữ S qua 3 cổng; khối tách 4 tầng + gói dữ liệu chạy; toà nhà cắt lớp; bản đồ nổi cách điệu; đường hầm màn hình (chỉ làm cảnh chèn 1–4 s) |

## 8. Lệnh CLI hay dùng

```bash
npx --yes hyperframes@0.8.159 check               # lint + kiểm tĩnh
npx --yes hyperframes@0.8.159 preview             # Studio cho người duyệt
npx --yes hyperframes@0.8.159 snapshot <dir> --frames 8 --no-end --no-browser-gpu --describe false
npx --yes hyperframes@0.8.159 render -o out.mp4 --fps 30 -q delivery
npx hyperframes catalog --query "whip pan"        # tra registry trước khi tự dựng hiệu ứng
npx hyperframes beats <nhạc>                      # lưới beat nhanh (đối chiếu pha kick)
```
Ứng viên registry đã dùng/đáng thử: `whip-pan-cut`, `flash-through-white`, `light-leak`, `cinematic-zoom`, `iris-reveal`, `text-match-cut`, `caption-kinetic-slam`, `sheet-spring-up`, `parallax-device-dive`, `grid-pixelate-wipe`, `glitch` (rất tiết chế).

**Ghim cả lúc render (Calokid, 11/2026):** gọi `npx hyperframes …` không ghi phiên bản thì npx có thể tự nâng bản giữa hai lệnh (check chạy 0.9.12, render đã thành 0.9.13). Luôn gọi `npx hyperframes@<x.y.z>` cho check, snapshot và render. Nếu bản đã nhảy, chạy lại `check` bằng đúng bản sẽ render, rồi xem khung trích từ file render.

## 9. Mốc clip footage theo lưới khung hình (từ ghost-editor, 11/2026)

Áp cho mọi `<video>`/`<audio>` cắt từ footage hoặc clip AI (take, khung giữ, matte, chuyển cảnh).

- `data-start`, `data-duration` = **số khung / fps, cắt bớt (floor) ở 6 chữ số thập phân**, không làm tròn: 2 khung @30 = `0.066666`.
  - `0.067` làm clip hiện trễ một khung. `0.066667` làm lặp khung đầu. Lý do: trình render chỉ bắt mốc bắt đầu khi lệch dưới 0,001 khung, và lấy khung video theo floor((t − start) × fps).
  - Hàm của ghost-editor (`scripts/build.mjs`): `const fgrid = (frames) => (Math.floor((frames / FPS) * 1e6) / 1e6).toFixed(6);`. Tính mốc bằng **số khung nguyên** trước rồi mới đổi ra giây.
- Cắt hình và tiếng riêng (ffmpeg rồi mới đưa vào khuôn): đưa mọi đoạn về lưới khung trước, cắt **cả hình lẫn tiếng ở cùng mốc đã làm tròn**. Nếu mỗi đoạn tự làm tròn thì giọng trôi sớm dần: ghost-editor đo được 43–54 ms sau 23 đoạn.
- Cắt ffmpeg để khớp mốc trên: `-ss` = thời điểm khung chính xác 6 chữ số, `-t` ngắn hơn nửa khung.
- Kiểm: số khung hình = số khung tiếng (lệch 0), như ở `08-kiem-tra-qa.md` §1.
- Trạng thái: luật lấy từ repo ngoài, **chưa thử trên khuôn FiSoft**. Khuôn chỉ có đồ hoạ + TTS thì không cần.
