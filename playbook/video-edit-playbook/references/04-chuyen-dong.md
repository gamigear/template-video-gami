# 04 · Chuyển động, chuyển cảnh, GSAP

Con số mặc định để lệch **có chủ đích**, không lệch vô tình. Nguồn: whaleyxbt/claude-motion, Herk Edit Kit `MOTION_PHILOSOPHY.md`, howseen-ai/claude-motion-design, product-launch-motion v1, motion-prompt, charlie947; đã áp vào 13 khuôn FiSoft và được duyệt.

## 1. Bảng số mặc định

| Việc | Con số / quy tắc |
|---|---|
| Đường cong vào | `cubic-bezier(0.16, 1, 0.3, 1)` (≈ `expo.out`) |
| Đường cong ra | `cubic-bezier(0.6, 0, 0.9, 0.35)`; thời gian ra ≈ ½ thời gian vào (0,35–0,55 s so với 0,7–1,25 s) |
| Chuyển giữa hai trạng thái | `cubic-bezier(0.65, 0, 0.35, 1)` |
| Độ trễ nối tiếp (stagger) | từ 0,09 s · thẻ/mục danh sách 0,2–0,25 s · chấm/vòng 0,06 s |
| Gõ chữ | 0,035 s/ký tự; con trỏ nhấp nháy ~2,4 Hz khi chờ |
| Lò xo / overshoot | chỉ hơi vượt (back ≤ 1.2; tắt dần ≥ 0,72); chữ lớn, logo, camera **không vượt**; không nảy kiểu hoạt hình |
| Giữ để đọc | ≥ 1 s sau khi chữ đứng yên + 0,25 s cho mỗi từ sau từ thứ 3; câu CTA ≥ 2 s (≥ 3 s an toàn hơn) |
| Linear | chỉ cho chuyển động liên tục (xoay, trôi nền), không cho thứ bắt đầu/dừng |

Đối chiếu đo được (EditAtlas `video-breakdown`, 12 demo motion graphics công khai: logo, tiêu đề, biểu đồ, banner, 10/11/2026):

- Phần tử vào trong 0,3–0,9 s, kiểu "nhanh rồi lắng" (ease-out).
- Khung giữ **đứng yên hoàn toàn 50–90 % thời lượng shot**.
- Ra bằng cách **đảo ngược lúc vào**, tăng tốc dần (ease-in). Ví dụ một logo sting: vào 0,7 s, đứng yên 71 %, ra 0,8 s.
- Các chữ/mảnh cách nhau ~0,15 s. Banner kết bằng đúng khung đầu để chạy vòng.

Con số này khác bảng trên ở hai chỗ:

- **Thời gian ra:** ở đây ≈ thời gian vào, bảng trên lấy ≈ ½.
- **"Đứng yên":** chỉ hợp logo/banner không có lời. Dưới lời đọc vẫn theo luật "không khung nào đứng yên tuyệt đối" (§2).

Chưa A/B, nên đừng đổi khuôn đã duyệt.

Từ điển ease có thời lượng (Herk): ra `power2.in` 0,2–0,33 s · vào `power2.out` 0,2–0,5 s · quét camera `power2.inOut` 1,2–2,3 s · giữ linear 0,4–0,65 s · thẻ đáp `back.out(1.2–1.5)` 0,3–0,5 s, **một lần mỗi cảnh**. Không dùng `gsap.defaults()` toàn cục.

Đặt ba đường cong thành tên chung bằng CustomEase (một lần ở root):

```js
gsap.registerPlugin(CustomEase);
CustomEase.create("vao",    "0.16,1,0.3,1");
CustomEase.create("ra",     "0.6,0,0.9,0.35");
CustomEase.create("chuyen", "0.65,0,0.35,1");
CustomEase.create("loXo",   "M0,0 C0.2,1.1 0.4,1.04 1,1"); // vượt nhẹ dùng chung
```

## 2. Nguyên tắc nhịp

- **Mỗi lúc một thứ chuyển động chính**; một tiêu điểm mỗi khung. Không bật hai phần tử độc lập cùng lúc (một thứ, ngừng, thứ kế).
- **Chữ không di chuyển trong lúc đang được đọc.**
- **Cảnh sau bắt đầu hiện trước khi cảnh trước rời hẳn**; không để khung trống giữa hai cảnh.
- **Đổi chữ trong cùng một khung:** chữ cũ ra sớm và ngắn (kèm nhòe nhẹ), chữ mới vào sau; không để hai chữ chồng nhau ("AAccepptd").
- **Không khung nào đứng yên tuyệt đối** trừ khung kết: giữ chuyển động nhỏ (con trỏ nhấp nháy, nền trôi vài px/s, thanh tiến độ, đợt sáng thứ hai). Dưới lời đọc dùng kiểu "chạy một lần rồi đứng", không chạy vòng.
- **Khung 0 là ảnh có nội dung** (chữ hook), không đen/trống.
- **Điểm nhấn "chạm đất" đúng từ**, không phải "bắt đầu" đúng từ: bắt đầu tween sớm bằng thời lượng tween vào (tối đa 0,5 s) để khung kết của hiệu ứng trùng lúc đọc từ then chốt. Nhãn phụ thì bắt đầu ở từ − 0,06 s là được.
- Dung sai hình neo vào từ: hiện **từ 0,2 s sau đến 1,8 s trước** từ neo; khuyến nghị dẫn trước 0,5 s. Hình sớm quá 1,8 s là lỗi riêng.
- Dấu tích / nhãn chỉ rơi **sau khi mục tiêu đã thấy 0,10–0,25 s**.
- Tổng thời lượng hình chèn ≥ lời đọc + 1 s; giữ khung cuối ≥ 1 s.
- **Vừa khe giọng:** khi độ dài cảnh do WAV quyết định, **kéo/cắt phần giữ**, không kéo phần vào/ra. Chữ vào xong đứng ở trạng thái giữ. Chỉ khi khe ngắn hơn vào + ra mới co đều, và ghi vào báo cáo.
- **Thay một hiệu ứng theo góp ý:** giữ nguyên mốc bắt đầu, độ dài và cách bàn giao với cảnh trước/sau; chỉ đổi chuyển động.
- Mỗi tween ra ghi chú tên tween vào tương ứng ở cảnh kế ("không gọi được tên tween cặp đôi thì chưa thiết kế xong chỗ nối").
- **Một quyền opacity cho mỗi phần tử** trong mỗi cửa sổ thời gian (hai tween cùng opacity → nhấp nháy ~10 Hz).
- Camera và wipe chạy **nối tiếp**, không đồng thời. Nhãn cách mép ≥ 60 px. Đạo cụ rời đi về opacity 0, không 0,3.
- Mọi tween trong cảnh **kết thúc trước mốc cắt**. Thời điểm xong muộn nhất = start + delay lớn nhất + duration, phải trước mốc cắt.

## 3. Chuyển cảnh

- **Mỗi lần đổi cảnh chỉ MỘT chuyển cảnh lớn**, không lặp cùng một kiểu hai lần liên tiếp. Trong cảnh dùng chuyển động nhỏ (spring pop, stagger, punch-in).
- Tra registry trước khi tự dựng: `npx hyperframes catalog --query "..."`. Ứng viên đã dùng: `whip-pan-cut`, `flash-through-white`, `light-leak`, `cinematic-zoom`, `iris-reveal`, `text-match-cut`, `caption-kinetic-slam`, `sheet-spring-up`, `parallax-device-dive`, `grid-pixelate-wipe`, `glitch` (rất tiết chế), các khối `transitions-*`.
- **Đảo độ sáng hoặc độ bão hoà mỗi lần đổi cảnh** (thẻ trung tính ↔ cảnh tràn màu nhấn; tối ↔ giấy) để mắt biết "sang đoạn mới" mà không cần chuyển cảnh lớn.
- Chuyển cảnh "thu nhỏ vào màn hình điện thoại" cần `z-index` cho cảnh đang thoát.

## 4. Nhịp UI cho màn hình phần mềm mô phỏng

Theo gói `ui` của motion-prompt, để thao tác trông như phần mềm thật chứ không như hoạt hình:

| Thành phần | Nhịp |
|---|---|
| Modal | nền mờ 40 %, hiện 0,3 s hơi phóng |
| Toast | trượt vào 0,35 s, tự tắt sau 2 s |
| Toggle | 0,2 s |
| Tabs | gạch chân trượt 0,25 s + nội dung cross-fade 0,2 s |
| Accordion | 0,35 s + mũi tên xoay 180° |
| Skeleton | vệt sáng quét 0,9 s/lần |
| Badge | nảy 0,3 s |
| Empty state | 0,35 s |
| Con trỏ | đặt **trong** node camera; gốc zoom đúng vào nút bấm; click = scale 0,9 → 1 kèm tiếng click đúng khung |

Thêm: **để bóng mờ trạng thái đầu** khi một vật đổi hình để mắt theo; **một vật đổi hình** thay vì mờ chuyển hai ảnh; quy ước chữ trên nút nói đúng việc xảy ra và giữ một tên suốt luồng ("Duyệt" → "Đã duyệt").

**Zoom và tín hiệu chú ý trong demo màn hình** (OpenMontage `screen-demo`, chưa áp thử): độ phóng theo cỡ vật — nút nhỏ 2,0–3,0×, hộp thoại 1,4–2,0×, kết quả cả trang 1,0–1,3×; chuyển zoom 0,8 s ease-in-out; tối đa 2 tín hiệu chú ý cùng lúc, **khoanh hoặc zoom, không cả hai**; tín hiệu hiện ngay trước thao tác, tắt nhanh sau đó, không chung chỗ phụ đề; con trỏ to 1,5–2× bình thường, vòng ~50 px; mỗi jump cut thêm cú đẩy 1,0→1,02×; dữ liệu thật che mờ.

## 5. Sáu công thức hiệu ứng đáng dùng (charlie947 `references/effects.md`)

Nhịp: sớm 0–0,8 s / giữa 0,8–1,4 s / muộn 1,4–2,2 s.

| # | Tên | Công thức |
|---|---|---|
| 02 | Ô tìm kiếm → kết quả | ô mở rộng trước rồi mới gõ (~0,75–1,2 s); 3 kết quả nhô lên 14 px lần lượt từ 1,1 s; mỗi kết quả một dữ kiện thật |
| 05 | Cột → đường | cột biến thành đường nối đỉnh, giá trị không đổi |
| 06 | Zoom bảng điều khiển | 4 góc ngắm màu nhấn bám quanh ô trong 0,9 s đầu → phần còn lại tối đi → ô phóng lên **từ đúng vị trí thật**, đường gạch nối góc |
| 14 | Kính lúp | làm nét một dòng báo cáo, phần còn lại nhoè |
| 15 | Đường chảy | xung sáng vẽ đường; nút **đáp lại khi xung tới** bằng vòng lan; đợt xung thứ hai giữ đoạn giữ sống |
| 16 | Logo hạt | đóng CTA (chỉ khi phong cách cho phép hạt) |

## 6. GSAP plugin (gsap 3.13+ mọi plugin miễn phí, kể cả thương mại)

Cài local, cùng phiên bản lõi, không CDN:

```bash
cd /tmp && npm pack gsap@3.15.0 && tar xzf gsap-3.15.0.tgz
cp package/dist/{DrawSVGPlugin,CustomEase,MotionPathPlugin,MorphSVGPlugin,SplitText}.min.js <dự-án>/assets/
```

Nạp sau `gsap.min.js`, gọi `gsap.registerPlugin(...)` một lần trước khi dựng timeline. Giữ dòng `@license` đầu file.

| Plugin | Tất định khi seek? | Dùng cho |
|---|---|---|
| DrawSVG, MorphSVG, MotionPath, CustomEase, CustomBounce, TextPlugin, Physics2D, SplitText | ✅ | vẽ nét, biến hình icon, chấm chạy theo đường, ease chung, tách chữ |
| Flip | ✅ nếu tạo tween lúc dựng và đưa vào `tl` | đổi bố cục |
| **ScrambleText** | ❌ gọi `Math.random` mỗi lần cập nhật | tự viết: chọn ký tự bằng `hash(chỉ số khung, vị trí ký tự)` (~15 dòng) |
| **CustomWiggle `type:"random"`** | ❌ | các kiểu khác (`easeOut`, `easeInOut`, `anticipate`, `uniform`) thì được |
| **RoughEase** | ❌ trừ khi `randomize:false` | |
| ScrollTrigger, ScrollSmoother, Observer, Draggable, Inertia, GSDevTools | không liên quan video | |

Mẹo và bẫy đã gặp:

- **DrawSVG thay cho tự đo `getTotalLength` + `strokeDashoffset`.** Tự ẩn nét bằng dash với `stroke-linecap: round` vẫn vẽ đầu nét thành **chấm tròn lộ ra trước khi nét được vẽ**. DrawSVG `"0%" → "100%"` ẩn sạch. Rút nét về `"100% 100%"` vẫn để lại một chấm → `autoAlpha: 0` cả SVG sau đó. Vẽ "từ giữa ra": `drawSVG: "50% 50%" → "0% 100%"`.
- **MorphSVG:** dây rối → đoạn thẳng bằng `shapeIndex: 0`, cùng ease/thời gian với vật đi kèm; xong thì ẩn dây morph, bật nét thật để các bước sau giữ nguyên.
- **MotionPath:** chấm chạy trên chính đường đang vẽ (`start 0 → end 1`), cùng thời gian + ease với `drawSVG` của đường đó.
- **SplitText `mask:"lines"` cắt dấu tiếng Việt** (mặt nạ `overflow:hidden` cao đúng một dòng). Sửa:
  ```js
  gsap.set(split.masks, { paddingTop: "0.22em", marginTop: "-0.22em", paddingBottom: "0.12em", marginBottom: "-0.12em" });
  ```
- SplitText tách **theo dòng** phải chạy sau khi font tải xong (dòng ngắt theo font dự phòng nếu chưa có). Dựng timeline trong `document.fonts.load(...).then(...)` và **gán `window.__timelines[id]` ở cuối callback**. Tách `words`/`chars` không cần đo nên không vướng.
- Chuỗi tiếng Việt chuẩn hoá `.normalize("NFC")` trước khi đưa vào HTML (NFD làm dấu tách khỏi chữ khi tách ký tự).
- `from`/`fromTo` của plugin cũng áp giá trị "from" ngay lúc dựng. Trạng thái ẩn đặt bằng `gsap.set(..., { drawSVG: "0%" })` lúc dựng; tween về sau dùng `immediateRender:false`.
- Đếm số: lõi GSAP tween `innerText` + `snap` là đủ, không cần plugin (chỉ số có thật).
- Không tween `letterSpacing` (lint HyperFrames báo lỗi) → dùng scale/opacity.

## 7. Danh sách cấm

- Tiêu đề giữa khung trên nền gradient; mọi thứ cùng mờ dần vào một lúc.
- Glow trên UI, hạt bay, emoji, gradient cầu vồng, nảy kiểu hoạt hình.
- Glitch tách RGB, grain/vignette/bloom mọi cảnh (thẩm mỹ showreel cắt theo nhạc, không hợp video dẫn bằng lời).
- `repeat: -1` cho nền (phá capture); `Math.random()`/`Date.now()`.
- Có tên trong từ điển hiệu ứng (particles, liquid, light sweep, impact shake…) **không có nghĩa là được dùng**.

## 8. Kiểm "vẻ thiết kế AI" (anthropics/skills › frontend-design)

Dùng làm câu hỏi kiểm khi thiết kế khuôn/phong cách mới (không áp ngược lên thiết kế đã duyệt):

1. Nền kem ~#F4F1EA + serif tương phản cao + nhấn màu đất nung.
2. Nền gần đen + một màu nhấn chói.
3. Bố cục kiểu báo giấy, nét mảnh, góc vuông.
4. Bộ thẻ SaaS: thẻ bo giống hệt nhau, bóng xám `rgba(0,0,0,.1)`, gradient trang trí.
5. "Khung mẫu": nhãn IN HOA giãn chữ trên mọi tiêu đề, chuỗi "A · B · C", số thứ tự 01/02/03 trang trí, tô màu/in nghiêng một từ trong tiêu đề.

Quy trình hai lượt: lập bảng token (4–6 màu hex có tên, vai trò từng font, bố cục ASCII) → tự đối chiếu với brief, phần nào giống mặc định thì sửa và nói lý do → mới dựng. "Dồn sự táo bạo vào một chỗ", phần còn lại tiết chế. Một câu nên ghi vào file thiết kế: *"file đặt ra cái nhìn, không đặt ra tham vọng; khi bảo làm hết sức thì làm hết sức"* (thiếu câu này bản đầu ra "quá lịch sự").

## 9. Ngôn ngữ chung khi brief và duyệt

- Góp ý bằng **tên hiệu ứng + ba thứ: bao lâu, mạnh bao nhiêu, cái gì chuyển động** ("tiêu đề cảnh 3: mask reveal 0,6 s thay cho fade"), không mô tả cảm tính.
- Spec mỗi hiệu ứng trong hướng dẫn của khuôn: cái gì chuyển động, thứ tự, mỗi phần bao nhiêu giây, đường cong nào, biên độ bao nhiêu px/độ/scale — **mọi số lấy từ code, không bịa**.
- **Duyệt bằng cách chọn:** khi mở khuôn mới, dựng một trang HTML cục bộ xếp các hiệu ứng ứng viên thành ô có số (snapshot hoặc vòng lặp ngắn); người dùng chọn số + ghi "cho cảnh nào"; chỉ dựng đúng số đã chọn.

## 10. Chuyển cảnh "trang đóng băng" trên footage thật (Calokid, 11/2026)
Người duyệt chê chuyển cảnh nhạt và chữ một kiểu. Bản được làm lại: 23 mốc cắt dùng 11 kiểu, chữ dùng 15 hiệu ứng.
- **Cách làm.** Trích đúng khung cuối mà cảnh cũ hiện trước mốc cắt T.
  - Công thức: `k = ceil(T·fps) − 1`; khung nguồn `floor((k/fps − đầu_slot)·fps)`.
  - File cảnh thường dài hơn slot, nên **không** lấy khung cuối file.
  - Nếu cảnh có push-in, phải áp thêm scale của khung đó.
  - Đặt ảnh này đè lên cảnh mới rồi tween nó đi: lật, tách đôi, đẩy, zoom. Không cần hai video chạy chồng nhau.
  - Đo chỗ nối: lấy khung trước và sau T, chênh trung bình ≈ 2,7/255 là đạt.
- **Lật trang quanh gáy trái phải lật RA SAU** (rotationY +90, perspective ≈ 1,6 × chiều rộng khung, `power1.in` 0,5 s).
  - Lật về phía người xem (−90) thì trang phình to, che kín khung tới tận cuối, nên gần như không thấy lật.
- **Không hòa tan hai cảnh cận mặt cùng một người.** Hai khuôn mặt lệch nhau sẽ thành bóng ma. Thay bằng lau chéo có dải sáng (clip-path polygon + dải gradient chạy theo mép).
- **Gán kiểu theo nghĩa, nhưng đa dạng.** Mở chương dùng một kiểu riêng lặp lại (ở đây là chém kiếm tách đôi, mỗi lần một góc). Khoảng lặng dùng kiểu mềm (vệt sáng, lau, trái tim). Mốc nhấn dùng chớp + rung.
  - Assert trong script: không kiểu nào lặp hai lần liền.
  - *Đã đổi:* bản đầu dùng lật trang cho mọi cắt trong chương (×7) và đẩy ×4. Người duyệt chê "đơn điệu". Bản sửa có 20 kiểu cho 23 mốc. Chỉ dấu hiệu cấu trúc mới được lặp: mở/khép sổ ×2, mở chương ×3. Mọi kiểu khác chỉ dùng 1 lần.
- **SFX.** Mỗi chuyển cảnh lớn một tiếng (giấy lật / whoosh / kiếm).
  - Để giữ trần 1 sự kiện / 2,2 s, gộp tiếng chuyển cảnh với tiếng chữ trong vòng 0,25 s, và bỏ các pop phụ.
- **Hiệu ứng chữ theo từng câu**, mỗi câu một kiểu: từ bật, chữ bay ráp lại, dạ quang tô, số chạy, gõ chữ, lật / gập thẻ, quất ngang, đập.
  - Sau khi đổi hiệu ứng, chạy `hyperframes check` mục craft `line_unread`. Kiểu gõ chữ và từ bật làm chữ hiện muộn, dễ thiếu thời gian đọc.
- **Công thức các kiểu thêm** (cùng dạng trang đóng băng, đều kiểm bằng snapshot):
  - **Quất ngang.**
    - Trang x 0 → −W, cảnh mới x W → 0, cùng `expo.inOut` 0,32 s, thêm 7 vệt sáng.
    - Hai bên phải chạy *đúng cùng* khoảng cách. Lệch 12 px là lộ khe nền.
  - **Lật lịch lên:** rotationX 0 → −90, origin mép trên, cùng phối cảnh với lật trang.
  - **Khối hộp:**
    - Trang rotationY 0 → −90, cảnh mới 90 → 0.
    - Cả hai dùng chung `transformOrigin: "50% 50% −W/2px"` và cùng perspective.
    - Góc khung lộ nền gốc, nên đặt nền gốc là màu tối của thương hiệu, không để đen.
  - **Cửa đôi và rèm:**
    - Cắt trang bằng `clip-path: inset(...)`, mỗi lá xoay quanh mép riêng của nó.
    - Mỗi lá cần một bản sao file ảnh. Dùng chung một file thì lint báo `duplicate_media`.
  - **Ô ghép:** lưới ô màu thương hiệu, stagger `grid` từ góc. Màu ô theo hoa văn tính sẵn (vd `(r+c)%5`). Màu băm ngẫu nhiên ra thành cụm lộn xộn.
  - **Xé giấy:**
    - Mép rách gồm các điểm cách nhau không đều 9–39 px, cộng sóng chậm và răng nhỏ, thêm lớp xơ trắng lệch ±11 px.
    - Điểm cách đều cho ra răng cưa giống cắt bằng kéo.
  - **Trái tim:**
    - Cảnh mới lộ qua clip-path polygon hình tim, tween scale 0,01 → 28 → 150.
    - Viền vàng là SVG `scale` quanh `svgOrigin` với `vector-effect: non-scaling-stroke`.
  - **Polaroid:** trang co lại trong viền trắng có bóng, nghiêng, rồi rơi xuống.
  - **Xoáy:** rotation −50 + scale → 0,08 cùng lúc.
  - Mỗi scene chứa trang đóng băng chia ít nhất 3 lane, tránh `timeline_track_too_dense`.
  - SFX theo chất liệu: giấy (lật, lật lịch), giấy xé, whoosh (quất, cửa, khối, rèm), pop (ô ghép), lấp lánh (trái tim, lau sáng).
