# 09 · Phim ngắn nhân vật bằng AI: khung ảnh → clip 10 s → hậu kỳ

Rút từ ~23 tập phim sitcom dọc làm 10/2026 (Google Flow · Gemini Omni 1.1 Flash). Triển khai tham chiếu: `/Volumes/Crucial SSD/Fisoft/output/phim-nhan-vat/` (gọi tắt `PNV/`). Nghiên cứu gốc: `/Volumes/Crucial SSD/Fisoft/Kịch bản phim ngắn nhân vật/NGHIEN-CUU-QUY-TRINH-PHIM-AI.md`. Cả hai chỉ còn trên SSD Crucial đã tháo (06/11/2026), không có trên ổ trong.

## 1. Quy trình end-to-end

| # | Bước | Công cụ | Con số, luật |
|---|---|---|---|
| 1 | Kịch bản | `.md`, mỗi tập **7 clip × 10 s + end card 3 s** ≈ 70–73 s | 10 s chứa ~40–46 chữ tiếng Việt; mỗi clip **một người nói chính, một hành động chính**. Khuôn 7 nhịp: nỗi đau → than + gọi người → người gỡ rối vào → đồng nghiệp xác nhận → gốc vấn đề (màn xanh) → giải pháp → CTA nhìn ống kính |
| 2 | Kinh thánh nhân vật | file `KINH-THANH-NHAN-VAT.md` + `khoi-mo-ta.json` (khối mô tả tiếng Anh, chèn qua placeholder `{TEN}`) | Mỗi người một khối cố định: tuổi, dáng, mặt, tóc, trang phục, phụ kiện. Bối cảnh cũng có khối. Ảnh gốc (chân dung + toàn thân + bối cảnh) **người dùng duyệt trước khi dùng** |
| 3 | Khung đầu/cuối (14 khung/tập) | ChatGPT web (mỗi khung một chat mới), dự phòng Codex CLI / Muse | Khung đầu = HEAD (ảnh tham chiếu + style) + khối nhân vật + SCENE. Khung cuối = chat mới, đính khung đầu, prompt EDIT: *"Locked-off camera… Do not zoom… Change ONLY this: …"*. Kiểm bằng bảng 7×2 + độ sáng trung bình |
| 4 | Prompt Flow | sinh từ script → `FLOW-PROMPT.md` + `flow-prompts.json` + `flow-inject.js` | Cấu trúc ở §2 |
| 5 | Sinh clip | Flow · Omni 1.1 Flash, khung đầu (+ cuối), 9:16, 720p, 10 s, x1 | **15 tín dụng/clip, ~105/tập**; lượt bị chặn được hoàn. Gửi liền 7 clip chạy song song, ~2 phút. Ra 720×1280, **24 fps**, 10,005 s, AAC, có dấu ✦ góc dưới phải. **Hỏi người dùng trước mỗi lần tiêu tín dụng** |
| 6 | Kiểm clip | `PNV/_tools/kiem-clip.py tao / soi / bao-cao` | §4 |
| 7 | Hậu kỳ (theo thứ tự) | `thay-man-xanh.py` → `cat-lap.py` → `che-loi.py lam` → `build.py` → `npx hyperframes render . -o work/hinh.mp4` → `mix.py` → `dong-dau.py` | Khung 1080×1920, 24 fps, −14 LUFS. Phần riêng mỗi tập chỉ nằm trong `noi-dung.json` + `phu-de.json` + `che-loi.json` |
| 8 | Chèn video giải pháp | `ghep.py` + `kiem-noi.py` | §6 |
| 9 | Giao | bảng duyệt ảnh, bản cũ giữ trong `work/` | Đăng: bật nhãn nội dung AI |

**Luật viết kịch bản cho clip AI:** mỗi clip 10 s có một khung đầu, một khung cuối, một hành động. Khung cuối clip N nên trùng khung đầu clip N+1 nếu hai cảnh nối liền. Tránh tay cầm vật nhỏ, máy quay chậm/đứng yên.

## 2. Prompt video (Flow/Omni)

```
<hành động trong cảnh>. Camera static, medium shot.
AUDIO: <khối giọng, chép y hệt ở mọi clip>. ~0.5s, <cách nói>: "<lời nguyên văn>". <Foley>.
All dialogue is spoken in Vietnamese … exactly the words in quotes, nothing added, nothing skipped,
nothing repeated, with accurate lip-sync. No other voices, no background chatter, no narration, no music.
Realistic room tone and natural Foley… bright high-key daylight… one continuous shot with no cuts,
keep every person's face and clothing exactly as in the first frame. No subtitles, no on-screen text.
```

- **Mỗi shot một động tác máy** (dolly in, rack focus, orbit, whip pan…), viết thành câu riêng. Cuối prompt có thể thêm `Negative: subtitles, watermark, text overlay` và "No background music".
- Màn hình thiết bị cần thay ở hậu kỳ: *"Keep the tablet screen a flat solid green the whole time"*. Không thay thì *"screen always faces away from the camera"*. Giấy tờ: *"no readable text or numbers"*.
- **Thoại tiếng Việt: để Omni tự nói** — khớp môi tốt hơn lồng TTS (bản mấp máy môi rồi lồng tiếng có tiếng lẩm bẩm vô nghĩa). Nghiên cứu ban đầu khuyên ngược lại (Google chỉ đánh giá đầy đủ tiếng Anh), nhưng thử thật thì Omni đạt. Hệ quả: **phụ đề theo lời thật trong clip, không theo kịch bản**; nghe lại từng clip.
- Ngoại hình nằm ở ảnh tham chiếu; prompt chỉ tả hành động. Khung đầu và khung cuối của cùng clip chỉ khác hành động + trạng thái đạo cụ, phần còn lại **giống hệt từng chữ** (cân nhắc prompt JSON có cấu trúc `scene / subjects[description, position, action] / style / color_palette / lighting / mood / camera`).
- Muốn đúng nguyên văn tuyệt đối (tên thương hiệu) thì TTS + lip-sync hậu kỳ, hoặc chấp nhận và nghe kỹ.

## 3. Bộ lọc nội dung ("người nổi tiếng / vi phạm chính sách")

**Hay bị chặn khi:** nhân vật nữ trẻ chiếm khung lớn, mặt chính diện rõ nét; prompt có "looks into the lens" hoặc đẩy máy vào mặt; prompt ghi tên riêng/vai ("secretary"); khung toàn thân thấy chân + giày cao gót; dùng cả khung đầu + cuối (bị chặn nhiều hơn chỉ khung đầu). Mỗi tài khoản lọc gắt khác nhau; có lượt chạy tới ~7 % rồi mới bị chặn ở bước kiểm đầu ra.

**Cách xử lý hợp lệ, thử theo thứ tự** (không dùng công cụ vượt chống bot):

1. Bỏ tên và vai, gọi bằng ngoại hình: "the young woman in a pink shirt", "the man".
2. Máy đứng yên, bỏ push-in. Thay "looks into the lens" bằng "turns toward the viewer where she stands".
3. Chỉ dùng khung đầu, bỏ khung cuối. Cảnh CTA mặc định chỉ khung đầu.
4. Vẽ lại khung (người dùng duyệt): nhân vật nhỏ ~38–45 % chiều cao khung, mặt nghiêng 3/4; hoặc quay lưng 3/4; CTA cắt cỡ trung ngang hông, không thấy chân. Thử lại cùng khung hay mượn khung tập khác vẫn bị chặn — phải vẽ lại.
5. Công cụ tạo ảnh từ chối cảnh "giận/quát": tả "nghiêm, tập trung, đang trình bày", để model video diễn cơn giận trong lúc chuyển sang khung cuối.

## 4. Kiểm clip trước hậu kỳ

- **Cổng tiền kiểm trước khi bấm tạo (tốn tín dụng):** beat có mục đích biên tập; thời lượng tính từ kịch bản; mỗi câu thoại xuất hiện **đúng một lần**; một neo nhân vật rõ cho mỗi người + tối đa một neo bối cảnh; trục không gian, trái/phải màn hình, tư thế, **trạng thái đạo cụ** đã ghi; không có job trùng đang chạy.
- **Sau 2 lần hỏng cùng một lỗi: đổi cấu trúc shot / cách tham chiếu / ràng buộc prompt**, không đổi seed nữa.
- Hết giờ chờ: dò lại trạng thái, URL tải hỏng thì lấy URL mới — **không gửi lại lệnh tạo** (tốn tín dụng, không an toàn khi lặp).
- **Sổ tín dụng:** mỗi lần bấm tạo ghi một dòng CSV (giờ, tài khoản, tập-clip, chế độ, số dư trước/sau, kết quả hoặc bị chặn) — để đối soát khi số dư tụt không rõ lý do (đã gặp: 85 → 1 trong một ngày). Không bao giờ tự thử lại một lệnh trả phí; tối đa 3 lần bị loại cho một mẫu rồi đổi cách. FiSoft đã làm ngày 02/11/2026: `output/phim-nhan-vat/_chung/so-tin-dung.py` + `SO-TIN-DUNG-FLOW.csv`.
  - Báo cáo cho biết chỗ số dư "trước" của lượt sau khác số dư "sau" của lượt trước, tức tín dụng mất ngoài sổ.
  - Báo lượt có số tiêu khác số clip qua × 15. Lượt bị chặn hoặc lỗi chung được hoàn, nên tiêu thật phải bằng số clip qua × 15.
  - Báo clip đã hỏng từ 3 lần trở lên.
  - Hai số dư phải đọc trên Flow, không ước. Lần ghi bù đầu tiên lộ ra một khoản 40 tín dụng chỉ do số ước sai.
- `kiem-clip.py`: ảnh ghép 4 khung/s + dạng sóng + từ whisper cho mỗi clip.
  - Cắt cảnh: `select='gt(scene,0.08)'` — tông trắng sáng có điểm scene thấp (cú cắt thật chỉ 0,144), ngưỡng 0,3 sẽ sót. Không dùng `-v error` (giấu log).
  - Lời theo từ: `whisper-cli -m ggml-small.bin -l vi -ml 1 -sow -oj`.
  - Nghi lặp: cụm 2–8 từ liền nhau giống nhau; whisper hay ép lần lặp thứ hai về độ dài 0 s → dấu hiệu lặp thật. So kịch bản bằng `difflib.SequenceMatcher` (% khớp, chữ thiếu/thừa). Tiếng nền = phân vị 10 của RMS 50 ms.
  - Chấm 6 tiêu chí 0–10 (nhân vật, đúng prompt, chuyển động, độ nét, liền mạch, bố cục). CRITICAL kéo tiêu chí xuống ≤ 3, HIGH ≤ 6. **Có CRITICAL hoặc TB < 6 → TẠO LẠI; có HIGH → DÙNG + SỬA HẬU KỲ; TB < 7,5 → XEM LẠI; còn lại → DÙNG.**
  - Chi tiết nhỏ (kính, ngón tay) dễ báo nhầm trên ảnh lưới → phóng to (`soi --t … --vung x,y,w,h`) trước khi ghi lỗi. Cho agent **chấm mù** (không đọc ghi chú) rồi mới đối chiếu.
  - Kết quả thực tế: bắt 10/11 lỗi lời đã biết + 4 lỗi hình mà người làm hậu kỳ chưa thấy.

## 5. Lỗi clip AI hay gặp và cách xử lý

| Lỗi | Xử lý |
|---|---|
| Nói lặp cụm/câu | **Cắt hẳn cả hình lẫn tiếng** (chỉ tắt tiếng thì môi vẫn mấp máy). Bỏ lần nói thứ nhất, giữ lần sau (có ngữ điệu kết câu). Đoạn sau mối cắt phóng 4 % để che nhảy hình |
| Vấp, thêm/nuốt chữ, đọc sai tên thương hiệu | Cắt nếu được, không thì tạo lại. Tên thương hiệu luôn nghe bằng tai (ASR nghe nhầm thường xuyên) |
| Người đi xuyên ghế/bàn | Cắt đoạn đó (chỗ không lời) + chớp sáng ở mối. Phòng từ prompt: "She does not walk around or through the desk" |
| Clip tự cắt cảnh, nhảy hình | Chớp sáng + phóng đúng mối → thành cú cắt có chủ ý |
| Nền biến dạng (cửa kính hiện rồi tan) | Vá bằng nền sạch = trung vị các khung lành (chỉ khi máy đứng yên) |
| Người ở nền đổi mặt | Làm mờ vùng elip mép mềm, tăng dần (giả lấy nét nông); hộp chữ nhật sẽ lộ mép |
| Mặt nhân vật chính trôi | Hậu kỳ không cứu được: tạo lại hoặc người dùng chấp nhận |
| Watermark ✦ góc dưới phải | `delogo` + đóng dấu thương hiệu nhỏ. **Mọi cú phóng phải neo quanh tâm watermark**, neo giữa khung thì ✦ thò ra dưới dấu |
| Đuôi clip có tiếng ngân lạ (~600–750 Hz), đầu/đuôi im lâu | Cắt đuôi/đầu |
| Tiếng nền > −47 dB (clip sạch −49…−60) | Khử ồn hoặc phủ room tone, nghe kỹ chỗ nối |
| Lời vào trễ hơn mốc prompt | Lấy mốc theo dạng sóng + khẩu hình, không theo whisper |
| Chân ló trước bàn khi người đứng sau bàn | Prompt: "desk occupies only the LEFT two-thirds… she stands on open floor to the RIGHT, nothing in front of her" |

## 6. Kỹ thuật hậu kỳ

**Trục thời gian tham số hoá (`tg.py`):** mọi mốc (phụ đề, chữ, SFX) ghi bằng **giây trong clip gốc**; `at(c, t)` đổi sang giây trên phim, trừ phần đã cắt trước t. Sửa đoạn cắt thì mọi thứ tự dời theo. Chọn file ưu tiên `-che` > `-cat` > `-man` > gốc.

**Cắt lặp + punch-in neo watermark (`cat-lap.py`):**
```
[0:v]trim=a:b,setpts=PTS-STARTPTS,scale=iw*1.04:ih*1.04,crop=720:1280:24:46,setsar=1[v1]
[1:a]atrim=a:b,asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st=<dài-0.025>:d=0.025[a1]
[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]        → libx264 -crf 14 -r 24, aac 256k
```
Neo phóng quanh điểm (ax, ay): `crop=W:H:ax*(s-1):ay*(s-1)` (vd tâm ✦ (600, 1160) trên 720×1280, s = 1.04 → `crop=720:1280:24:46`).

**Che lỗi hình (`che-loi.py`, đặc tả JSON):** `va` (nền sạch = `np.median` các khung chỉ định, mặt nạ chữ nhật mép mềm Gaussian, lên/xuống 0,2 s) · `mo` (Gaussian σ 5–7, tăng dần 0,6 s, `elip:true`) · `cat` + `chop` (chớp trắng 5 khung 0,35/0,8/0,85/0,5/0,2, phóng 8 % lùi về 4 % trong 0,4 s ease cubic, giữ 4 %; whoosh −18 dB ở mối). `che-loi.py mau` xuất ảnh GỐC | SAU để **duyệt trước khi áp**.

**Thay màn xanh (`thay-man-xanh.py`):** mặt nạ `G − max(R,B) > 40 & G > 90` → 4 góc bằng argmin/argmax của x+y và x−y → mượt theo thời gian (trung vị ±2 khung, chỉ khi vùng xanh ≥ 8000 px và tâm lệch < 40 px) → homography ảnh màn → alpha `clip((g−20)/50)` → khử ánh xanh viền `G ≤ max(R,B)+6`; vệt xanh phản chiếu trên bàn `G ≤ 0.97·R`.

**Dựng chữ (HyperFrames):** các `<video class="clip">` đều `muted` (âm trộn riêng bằng ffmpeg). Chữ màn hình 3 kiểu: đập + rung, bật (`back.out`), trượt (`expo.out`). Vùng đặt trên 1080×1920: mặt nhân vật y 330–850 · chữ màn hình y 1000–1120 · phụ đề y 1330 (cảnh có tablet trên bàn: chữ lên y 190, phụ đề nâng lên y 1010). Xem lưới khung từng tập rồi mới chỉnh. Phụ đề có nhãn tên vai, mỗi vai một màu, nền dải bán trong suốt.

**Trộn âm (`mix.py`):**
```
# từng clip về -17 LUFS (loudnorm 2 lượt, linear=true)
loudnorm=I=-17:TP=-2:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true
# bus thoại: TRỘN THÊM anullsrc dài bằng cả phim → sidechain không dừng khi hết thoại (apad làm treo)
anullsrc=r=48000:cl=stereo -t TOTAL ; [..]amix=normalize=0,asplit=2[dlg][key]
# nhạc nền 3 đoạn theo mạch (hài → piano lúc gốc vấn đề → guitar sáng lúc giải pháp/CTA), mỗi đoạn −29…−30 LUFS, fade 0,8–2 s
[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=600:makeup=1[bgm]
volume='1+0.8*min(max((t-st)/0.8,0),1)':eval=frame            # dâng nhạc ở end card
# chốt: limiter ăn ~0,8 LU nên đặt −13,2 rồi limit → đo ra ≈ −14,1 LUFS, TP ≤ −1
volume=<-13.2-I>dB,alimiter=limit=0.891:attack=3:release=60:level=disabled
```
SFX căn theo **đỉnh** file: `adelay = t_sự_kiện − peak_offset(file)`.

Mọi nhánh (từng clip thoại, từng đoạn nhạc, từng SFX) kết thúc bằng `adelay=…,asetpts=N/SR/TB,atrim=0:TOTAL,apad=whole_dur=TOTAL`; ba lần `amix` đều `normalize=0:duration=first` (nhánh đầu luôn dài TOTAL); lệnh ffmpeg có `-nostdin` và `-t TOTAL`. Bản cũ `amix=duration=longest,apad,atrim` chạy tl-1 mất 150 s, bản vá 15 s, ra cùng mẫu âm (±2 LSB). Đã vá cả 21 `mix.py` ngày 02/11/2026. **Nhánh thoại có `loudnorm` nên không được bỏ `asetpts`** (`12-lenh-ffmpeg.md` §3).

**Đóng dấu thương hiệu (bước cuối, trên MP4 đã trộn, bỏ qua end card 3 s):**
```
[0:v]delogo=x=852:y=1692:w=96:h=96:enable='lte(t,DUR-3)'[v];
[v][1:v]overlay=x=900-overlay_w/2:y=1740-overlay_h/2:enable='lte(t,DUR-3)'
```

**Chèn video giải pháp giữa phim (khuôn đã chốt):** tình huống C01–C06 → lúc nhân vật trình bày, chạy **nguyên một video giải pháp toàn màn hình** (giọng đọc riêng, không cần khớp lời nhân vật, bỏ CTA riêng của video chèn) → quay lại C07 + end card; phim ~110 s. Thẻ sơ đồ nhỏ hay PiP 8 s bị đánh giá "chưa đủ thông tin".
```
[0:v]trim=0:CAT ; [1:v]trim=0:DAI3D ; [0:v]trim=CAT-0.3:DUR      (fps=24,scale=1080:1920,setsar=1,format=yuv420p)
[v1][v2]xfade=transition=fade:duration=0.3:offset=CAT-0.3[v12];[v12][v3]xfade=transition=fade:duration=0.3:offset=CAT+DAI3D-0.6[v]
[1:a]…,loudnorm=I=-14:TP=-1.5:LRA=11[a2] ; [a1][a2]acrossfade=d=0.3[a12];[a12][a3]acrossfade=d=0.3
→ PCM trung gian .mov → loudnorm 2 lượt −14 LUFS / TP −1,5 → AAC 192k
```
Mối nối nằm trong đuôi C06, không lấn vào lời C07; `CAT` đo lại từng tập; `DAI3D` = mốc bắt đầu cảnh CTA của video chèn. Kiểm: 8 khung quanh 2 mối nối + `ebur128=peak=true`.

Biến thể PiP (không chốt nhưng dùng được): phóng vào tablet `scale 1→1.5` 0,45 s `power3.in`, `transformOrigin` = % toạ độ tablet → mờ chéo 0,3 s sang cảnh chèn → khung tròn người nói khớp môi (cùng nguồn clip, `data-media-start`, `clip-path: circle()`, viền trắng 6 px) → phóng ngược ra.

## 7. Phản hồi đã chốt → luật chung

1. **Tông trắng sáng high-key:** độ sáng trung bình ~165/255, ánh ngày trưa, cân bằng trắng trung tính; cấm nắng chiều vàng/cam. Độ sáng lấy từ prompt, không nâng gamma sau khi tạo ảnh.
2. **Logo:** không dùng viên trắng chứa logo màu đầy đủ chữ ("quá xấu"). Dấu nhỏ đơn sắc cùng cỡ watermark gốc. Màn thiết bị: nền navy + logo trắng + quầng sáng nhẹ, không giả giao diện app.
3. **Duyệt ảnh mẫu trước khi áp hàng loạt** (logo, che lỗi, khung, khuôn hậu kỳ): áp 1 tập mẫu → chờ duyệt → nhân ra.
4. **Nhãn AI:** không chạy dòng "nội dung AI" suốt phim; giữ dòng chú nhỏ ở end card + bật nhãn AI khi đăng.
5. **Mặt nhân vật** AI dễ "đại trà": với nhân vật chính, xin ảnh mẫu mặt trước khi tạo; neo bằng **bộ 4 ảnh vàng** (chính diện, nghiêng trái, nghiêng phải, toàn thân thấy mặt) đã duyệt; không lấy ảnh vừa sinh làm tham chiếu mặc định; ghi `negative-rules` (điều không được xuất hiện).
6. **Thẻ phong cách bối cảnh 5 phần:** ảnh tham chiếu → phân tích thị giác (ánh sáng, chất liệu, độ sâu) → luật cốt lõi không đổi / luật được biến → mẫu prompt → cách sửa khi lệch (ghi cả các lần bị từ chối).
7. **Kịch bản sơ sài, thiếu nhạc nền đều bị chê** → luôn có nhạc nền theo mạch cảm xúc.
8. **Vận hành:** hỏi trước mỗi lần tiêu tín dụng; ghi URL chat của từng khung để tải lại; chạy `sync` sau mỗi lần chép file lên ổ ngoài; bản cũ cất `work/` hoặc `_log/`, không xoá.

## 8. Tự động hoá giao diện (ghi lại để khỏi mò)

- Tải khung lên Flow: patch `HTMLInputElement.prototype.click` để giữ ô chọn file, rồi upload 4 JPG mỗi lần. Gắn khung: gõ tên ảnh vào ô tìm, bấm thẳng kết quả để gắn vào ô Bắt đầu/Kết thúc. Tải clip: biểu tượng tải → 720p "Kích thước gốc".
- Chèn prompt vào ô soạn: `execCommand('insertText')` (`flow-inject.js`, hàm `F.put('C03')`).
- Trang ChatGPT: CSP chặn eval → nạp script bằng thẻ `<script nonce>`; tải ảnh qua canvas.
- Codex CLI tạo ảnh hàng loạt: `codex exec -i ref …` **bắt buộc `stdin=/dev/null`** (không thì treo); gói ChatGPT hết lượt Codex sau ~10 ảnh.
- Tải file > 10 MB lên Facebook qua trình duyệt điều khiển: chia 9 MB bằng `split`, đưa từng phần vào input file ẩn, ghép Blob bằng JS, kiểm SHA-256, gán vào input video bằng `DataTransfer`.
- **Không dùng:** công cụ vượt reCAPTCHA (FlowKit `hijack_bypass.js`), xoay vòng nhiều tài khoản + proxy, lái web app bằng cookie xuất ra (muse2api) — nguy cơ khoá tài khoản, trái điều khoản.

## 9. Script tái dùng (trong `PNV/`)

| Đường dẫn | Chức năng | Phụ thuộc / ghi cứng |
|---|---|---|
| `_tools/kiem-clip.py` | ảnh ghép kiểm clip, phát hiện lặp/cắt cảnh/tiếng nền, chấm 6 tiêu chí → BAO-CAO.md | ffmpeg, whisper-cli + ggml-small, numpy, Pillow; cấu trúc `<tập>/clip`, `khung/jpg`, `FLOW-PROMPT.md` |
| `_tools/che-loi.py` | vá nền, làm mờ, cắt + chớp theo JSON; ảnh trước/sau | numpy, Pillow, ffmpeg; 720×1280@24 + tâm ✦ ghi cứng |
| `tl-1/hau-ky/tg.py` | trục thời gian sau cắt | Python thuần |
| `tl-1/hau-ky/build.py` | sinh composition HyperFrames (clip, chữ, thẻ, phụ đề, CTA, end card) | HyperFrames, GSAP |
| `tl-1/hau-ky/mix.py` | chuẩn hoá clip, nhạc 3 đoạn, ducking, SFX căn đỉnh, −14 LUFS | ffmpeg, numpy |
| `tl-1/hau-ky/cat-lap.py` | cắt lặp + punch-in neo watermark | ffmpeg |
| `tl-1/hau-ky/thay-man-xanh.py` | bám 4 góc màn xanh, homography, khử ánh xanh | numpy, Pillow, ffmpeg |
| `tap-7/chen-3d/ghep.py`, `kiem-noi.py` | chèn video giữa phim (xfade/acrossfade 0,3 s), kiểm mối nối + LUFS | ffmpeg, Pillow |
| `_chung/thuong-hieu/dong-dau.py` | delogo + đóng dấu | ffmpeg; toạ độ 1080×1920 ghi cứng |
| `_tools/gen.py` | tạo ảnh hàng loạt bằng Codex từ jobs.json | Codex CLI có image_generation |
| `tl-11/_tools/prompts.py`, `flow_prompts.py` | mẫu prompt HEAD/END/EDIT; gói prompt Flow + `flow-inject.js` | Python thuần |
