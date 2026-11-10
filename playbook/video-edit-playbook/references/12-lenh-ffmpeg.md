# 12 · Sổ lệnh ffmpeg / ffprobe đã dùng thật

Mọi lệnh đã chạy thử trên macOS (Homebrew ffmpeg 9.0.1, zsh) ngày 02/11/2026 bằng file tổng hợp. Chữ HOA (`DUR`, `ST`, `N`…) là chỗ thay số; thay bằng biến shell thì **luôn viết `${DUR}`**, không `$DUR` (zsh, xem §8). Nguyên tắc chung: **đo trên file giao, không tin code**; mọi lệnh chạy nền thêm `-nostdin`.

## 1. Thông tin file (ffprobe)

```bash
# thời lượng (giây)
ffprobe -v error -show_entries format=duration -of csv=p=0 in.wav

# luồng hình: khổ, fps (giữ phân số), màu, xoay
ffprobe -v error -select_streams v:0 -of json -show_entries \
  stream=width,height,avg_frame_rate,pix_fmt,color_range,color_space,color_transfer,color_primaries:stream_side_data=rotation in.mp4

# có luồng âm không, sample rate, số kênh
ffprobe -v error -select_streams a -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 in.mp4
```

## 2. Trích khung và ảnh kiểm

```bash
# một khung tại t (đặt -ss SAU -i: trên bản nháp CRF cao, -ss trước -i ra khung rỗng ở điểm không phải keyframe)
ffmpeg -v error -y -i in.mp4 -ss 3.20 -frames:v 1 khung.png

# khung cuối (bọc đuôi clip để không lộ khung đen): lùi 0,25 s rồi ghi đè tới khung cuối.
# -sseof -0.04 KHÔNG ra ảnh nào với clip 24 fps (khung dài 0,042 s) — đã thử
ffmpeg -v error -y -sseof -0.25 -i in.mp4 -update 1 cuoi.png

# strip 10 khung liên tiếp quanh mỗi mốc cắt (bắt lớp kẹt, lớp ma, khung nháy)
ffmpeg -v error -y -i out.mp4 -vf "select='between(n,N,N+9)',scale=384:-1,tile=layout=5x2" -frames:v 1 -fps_mode passthrough strip.png

# strip dài đọc "chữ ký" chuyển động: các ô y hệt = dừng chết; một ô khác hẳn hai bên = nháy
ffmpeg -v error -y -i out.mp4 -vf "select='between(n,A,B)',scale=480:270,tile=layout=6x7" -frames:v 1 -fps_mode passthrough chu-ky.png

# phone sheet: mỗi giây một khung ở 360 px (và 200 px = cỡ ô khi lướt)
ffmpeg -v error -y -i out.mp4 -vf "fps=1,scale=360:-1,tile=layout=8x5" -frames:v 1 sheet-360.png
ffmpeg -v error -y -i out.mp4 -vf "fps=1,scale=200:-1,tile=layout=8x5" -frames:v 1 sheet-200.png

# phát hiện cắt cảnh trong clip AI (tông sáng có điểm scene thấp: cú cắt thật ~0,14 → ngưỡng 0,08).
# KHÔNG dùng -v error: metadata=print in ở mức info
ffmpeg -hide_banner -nostats -i clip.mp4 -vf "select='gt(scene,0.08)',metadata=print" -an -f null - 2>&1 | grep pts_time

# khung đen
ffmpeg -hide_banner -nostats -i out.mp4 -vf blackdetect=d=0.03:pix_th=0.06 -an -f null - 2>&1 | grep black_start

# thống kê độ sáng từng khung → khung phẳng (YHIGH−YLOW rất nhỏ = một màu trơn),
# khung nháy (YDIF khung n lớn và khung n+1 cũng lớn), độ sáng trung bình (YAVG) theo thời gian
ffmpeg -v error -i out.mp4 -vf "signalstats,metadata=print:file=stats.txt" -an -f null -
grep -E "pts_time|YAVG|YLOW|YHIGH|YDIF" stats.txt | head

# khớp vòng: so khung đầu với khung cuối (SSIM gần 1 = vòng lặp liền)
ffmpeg -v info -nostats -i out.mp4 -sseof -0.25 -i out.mp4 \
  -filter_complex "[0:v]trim=end_frame=1[a];[1:v]reverse,trim=end_frame=1[b];[a][b]ssim" -f null - 2>&1 | grep -o "All:[0-9.]*"
```

## 3. Trộn âm

**Stem SFX — đặt từng cue, mọi nhánh dài đúng `DUR`** (vá treo `amix`):
```bash
ffmpeg -nostdin -y -i pop.wav -i whoosh.wav -i riser.wav -filter_complex "
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-14dB,adelay=1230:all=1,asetpts=N/SR/TB,atrim=0:DUR,apad=whole_dur=DUR[c0];
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-13dB,adelay=4870:all=1,asetpts=N/SR/TB,atrim=0:DUR,apad=whole_dur=DUR[c1];
[2:a]atrim=2.9:4.3,asetpts=PTS-STARTPTS,afade=t=out:st=1.25:d=0.15,aformat=sample_rates=48000:channel_layouts=stereo,
     volume=-20dB,adelay=9100:all=1,asetpts=N/SR/TB,atrim=0:DUR,apad=whole_dur=DUR[c2];
[c0][c1][c2]amix=inputs=3:normalize=0:duration=first[out]" -map "[out]" -t DUR -ar 48000 -ac 2 sfx-stem.wav
```
- `adelay` tính bằng **ms = (t_sự_kiện − đỉnh/attack của file) × 1000** (đo bằng hàm ở `05-am-thanh-sfx.md` §4).
- `normalize=0` để amix không tự chia nhỏ mức; `duration=first` + mọi nhánh có `apad=whole_dur` + `-t DUR` → không treo. **Không bao giờ `apad` không giới hạn.**
- **`asetpts=N/SR/TB` ngay sau `adelay` là bắt buộc.** Đo 02/11/2026 (ffmpeg 9.0.1): nhánh có `loudnorm` phía trước thì khung đầu ra của `adelay` mang pts NOPTS, khung kế pts âm vô nghĩa. `atrim=0:DUR` coi đó là trước 0 s nên **cắt bỏ cả đoạn lặng chèn**, mà `amix` ghép theo số mẫu chứ không theo pts → mọi câu dồn về đầu file, không báo lỗi. File SFX giải mã thẳng (không loudnorm) thì pts vẫn đúng, nhưng cứ thêm `asetpts` cho mọi nhánh.
- Kiểm một đồ thị trộn mới: so với bản trộn cũ đã duyệt bằng số mẫu (khớp ±2 LSB, năng lượng lệch < −100 dB), hoặc thử nhánh đơn: sine 0,5 s + `adelay=2000` phải ra tiếng ở đúng 2,0 s.

**Nhạc nền lặp + hạ khi có giọng (sidechain):**
```bash
ffmpeg -nostdin -y -stream_loop -1 -i bed.wav -i voice-sidechain.wav -filter_complex "
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:DUR,afade=t=in:d=0.05,afade=t=out:st=DUR-1:d=1,volume=-11dB[m];
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur=DUR[k];
[m][k]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=450:makeup=1[out]" -map "[out]" -t DUR bgm-ducked.wav
```
- **Tín hiệu khoá (key) phải dài bằng cả video**: hết key thì sidechaincompress dừng ra tiếng. Cách 1: `apad=whole_dur=DUR`. Cách 2 (dùng ở phim AI): trộn key với `anullsrc=r=48000:cl=stereo` dài `DUR` bằng `amix=normalize=0`.
- Phim có thoại thật: `ratio=5:attack=30:release=600`, nhạc mỗi đoạn −29…−30 LUFS.
- **Bẫy bed có đuôi lặng:** `-stream_loop` lặp luôn đoạn lặng ở cuối file bed → video ngắn hơn file ăn trọn đoạn lặng, video dài hơn mất nhạc vài giây rồi nhạc bật lại đột ngột (FiSoft 11/2026: bed 40 s lặng từ 36,27 s → 111/224 reel kết thúc bằng ~2 s im lặng). Mở file bed bằng `silencedetect` + RMS từng 0,5 s trước khi dùng (nhạc có thể đã hết sớm hơn đoạn lặng: bed FiSoft hết ở 32 s, tắt dần tới 36,3 s). Nối vòng **theo ô nhịp**: tìm chu kỳ lặp (thường 8 ô nhịp; 120 BPM → 16 s), quét tương quan giữa nhạc tại t và t − chu kỳ, chọn t tương quan cao nhất (FiSoft: 30,58 s, 0,98), rồi `asplit` + `atrim=0:t+x/2` / `atrim=t−P−x/2:t+x/2` + `acrossfade=d=x:c1=tri:c2=tri` (x ≈ 0,06 s; hai bên gần như cùng tín hiệu nên dùng đường thẳng). Kiểm: sau chỗ nối, mẫu phải trùng mẫu trước đó đúng một chu kỳ; bước mẫu lớn nhất quanh chỗ nối không vượt mức trong nhịp. Fade-out 1 s cuối luôn có, không đặt điều kiện "video dài hơn bed". Ghi phiên bản cách trộn vào WAV (`-metadata comment=...`) để công cụ sinh lại stem biết stem nào đã cũ.

**Biểu thức volume theo thời gian:**
```
volume='min(1,max(0,max(A-t,t-B)/0.03))':eval=frame       # tắt tiếng đoạn [A,B], dốc 30 ms hai bên
volume='1+0.8*min(max((t-ST)/0.8,0),1)':eval=frame         # dâng nhạc +80 % trong 0,8 s từ ST (end card)
afade=t=in:d=0.025,afade=t=out:st=L-0.025:d=0.025          # mỗi đoạn cắt có tiếng: fade 25–30 ms hai đầu
```

**Chuẩn hoá từng clip/câu thoại về cùng mức (loudnorm 2 lượt, linear):**
```
loudnorm=I=-17:TP=-2:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true
```

**Chốt master trước loudnorm cuối:**
```
volume=<-13.2 − I_đo>dB,alimiter=limit=0.891:attack=3:release=60:level=disabled
```
`level=disabled` bắt buộc (thiếu thì alimiter tự kéo to). Limiter ăn ~0,8 LU nên đặt −13,2 → đo ra ≈ −14,1 LUFS.

## 4. Đo âm

```bash
# LUFS tích hợp + true peak, file stereo giao
ffmpeg -hide_banner -nostats -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12

# bản mono (đọc thấp hơn ~3 dB; lộ triệt pha)
ffmpeg -hide_banner -nostats -i out.mp4 -af "pan=mono|c0=0.5*c0+0.5*c1,ebur128=peak=true" -f null - 2>&1 | tail -12

# lượt 1 loudnorm: in JSON số đo để đưa vào lượt 2 (§6)
ffmpeg -hide_banner -nostats -i raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p'

# vùng có tiếng của một câu TTS → s0 = silence_end đầu, s1 = silence_start cuối
ffmpeg -hide_banner -nostats -i cau.wav -af silencedetect=n=-40dB:d=0.08 -f null - 2>&1 | grep -E "silence_(start|end)"

# SFX có thật sự nghe được không: RMS trong cửa sổ quanh cue, theo dải tần, so với cùng cửa sổ trên bản không SFX
ffmpeg -v info -nostats -i out.mp4 -af "atrim=0.05:0.35,highpass=f=2000,lowpass=f=8000,volumedetect" -f null - 2>&1 | grep mean_volume

# RMS theo cảnh (lặp cho từng [đầu, cuối] cảnh) → CTA thấp hơn đoạn lời > 3 dB = lỗi
ffmpeg -v info -nostats -i out.mp4 -af "atrim=START:END,volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"

# LUFS từng câu WAV (chênh > 1,5 LU → cân gain trước khi mix)
for f in audio/*.wav; do printf "%s " "$f"; ffmpeg -hide_banner -nostats -i "$f" -af ebur128 -f null - 2>&1 | grep -m1 -E "^ +I:"; done

# tiếng nền clip AI: phân vị 10 của RMS 50 ms (> −47 dB = ồn); làm bằng numpy trên PCM:
# ffmpeg -i clip.mp4 -ac 1 -ar 16000 -f f32le - | python3 -c "…np.percentile(20*log10(rms_50ms),10)…"
```

## 5. Cắt, nối, chuyển, che

```bash
# cắt bỏ đoạn [a,b] (cả hình lẫn tiếng) + punch-in 4 % neo quanh điểm (ax,ay) cho đoạn sau
#   công thức neo: crop=W:H:ax*(s-1):ay*(s-1)   (vd tâm (600,1160) trên 720×1280, s=1.04 → crop=720:1280:24:46)
ffmpeg -nostdin -y -i clip.mp4 -i clip.mp4 -filter_complex "
[0:v]trim=0:a,setpts=PTS-STARTPTS,setsar=1[v0];
[0:a]atrim=0:a,asetpts=PTS-STARTPTS,afade=t=out:st=a-0.025:d=0.025[a0];
[1:v]trim=b:10.0,setpts=PTS-STARTPTS,scale=iw*1.04:ih*1.04,crop=720:1280:24:46,setsar=1[v1];
[1:a]atrim=b:10.0,asetpts=PTS-STARTPTS,afade=t=in:d=0.025[a1];
[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 14 -r 24 -c:a aac -b:a 256k cat.mp4

# chèn đoạn B giữa A: hai mối mờ chéo 0,3 s (hình) + acrossfade 0,3 s (tiếng)
#   v1 = A[0,CAT]  v2 = B[0,DB]  v3 = A[CAT-0.3,DUR]   (mỗi nhánh: fps=24,scale=1080:1920,setsar=1,format=yuv420p)
[v1][v2]xfade=transition=fade:duration=0.3:offset=CAT-0.3[v12];
[v12][v3]xfade=transition=fade:duration=0.3:offset=CAT+DB-0.6[v];
[a1][a2]acrossfade=d=0.3[a12];[a12][a3]acrossfade=d=0.3[a]
# → xuất PCM trung gian (.mov pcm_s16le) rồi loudnorm 2 lượt về đích (§6)

# nối nhiều file cùng thông số, không encode lại (phải cùng codec, khổ, fps, timebase)
printf "file '%s'\n" a.mp4 b.mp4 c.mp4 > list.txt && ffmpeg -f concat -safe 0 -i list.txt -c copy noi.mp4

# xoá watermark góc + đóng dấu thương hiệu, bỏ qua end card 3 s cuối
ffmpeg -y -i in.mp4 -i dau.png -filter_complex "
[0:v]delogo=x=852:y=1692:w=96:h=96:enable='lte(t,DUR-3)'[v];
[v][1:v]overlay=x=900-overlay_w/2:y=1740-overlay_h/2:enable='lte(t,DUR-3)'" -c:a copy out.mp4

# phóng clip AI 720×1280 lên khung 1080×1920
-vf "scale=1080:1920:flags=lanczos,setsar=1"
```

## 6. Encode xuất (chuẩn reel)

```bash
# lượt 2 loudnorm ngay trên bản render, giữ nguyên hình
ffmpeg -nostdin -y -i raw.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=${I}:measured_TP=${TP}:measured_LRA=${LRA}:measured_thresh=${TH}:offset=${OFF}:linear=true,aresample=48000" \
  -c:a aac -b:a 192k -movflags +faststart out.mp4

# encode lại đầy đủ theo chuẩn reel-export (khi hình chưa đạt chuẩn).
# ffmpeg 9: chỉ -color_* ở đầu ra KHÔNG gắn được primaries/trc khi nguồn chưa có thẻ → thêm setparams (đã thử: ra bt709,bt709,bt709)
ffmpeg -nostdin -y -i in.mp4 -vf "setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709" -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 18 -preset slow -r 30 \
  -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart out.mp4

# video câm vẫn phải có luồng AAC
ffmpeg -nostdin -y -i cam.mp4 -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart out.mp4

# remux WAV master vào bản render (khi trình render encode lại âm nhỏ hơn master), rồi đo lại §4
ffmpeg -nostdin -y -i render.mp4 -i master.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t DUR -movflags +faststart out.mp4
```
Kiểm sau xuất: `ffprobe` (§1) ra `h264 high yuv420p tv bt709`, có luồng aac 48 kHz; `ebur128` (§4) ra −14 ±0,5 LUFS, TP ≤ −1 dBTP.

## 7. Video thật: HDR, xoay, fps

```bash
# HDR nếu color_transfer là smpte2084 (PQ) hoặc arib-std-b67 (HLG) → tone-map về BT.709 SDR
ffmpeg -nostdin -y -i iphone.mov -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" \
  -c:v libx264 -crf 18 -c:a aac -b:a 192k sdr.mp4

# hướng: đọc stream_side_data=rotation (§1), không tin tag "rotate" cũ. ffmpeg tự xoay khi encode lại (autorotate mặc định bật)

# đưa mọi đoạn về cùng fps trước khi nối -c copy (giữ phân số NTSC nếu nguồn là 30000/1001)
ffmpeg -nostdin -y -i in.mp4 -vf fps=30000/1001 -c:v libx264 -crf 18 -c:a copy cung-fps.mp4

# nền footage phủ tới hết reel: giữ khung cuối thêm 1 s cho đuôi nhạc / thẻ kết (06 §9; không dùng cho B-roll chèn)
ffmpeg -nostdin -y -i talk.mp4 -an -vf "tpad=stop_mode=clone:stop_duration=1.0" -c:v libx264 -crf 14 -g 30 nen-giu-cuoi.mp4
# kiểm 0,4 s cuối bản render không đen
ffmpeg -nostdin -sseof -0.4 -i out.mp4 -vf blackdetect=d=0.03:pic_th=0.98 -an -f null - 2>&1 | grep black_start
```
Cần ffmpeg có `libzimg`: kiểm `ffmpeg -filters | grep zscale` trước. **Bản Homebrew mặc định (9.0.1) trên máy FiSoft không có `zscale`** — chuỗi trên sẽ báo lỗi filter không tồn tại; cần bản ffmpeg build kèm libzimg trước khi xử lý video HDR.

## 8. Bẫy shell / ffmpeg

| Triệu chứng | Nguyên nhân · cách sửa |
|---|---|
| ffmpeg treo không thoát | `apad` không giới hạn, hoặc `amix=duration=longest` + `apad`; hoặc ffmpeg chờ stdin khi chạy nền → `apad=whole_dur`, `duration=first`, `-t DUR`, `-nostdin` |
| Thoại/SFX dồn hết về đầu file, phần sau lặng (không báo lỗi) | `atrim` sau `adelay` cắt mất đoạn lặng chèn vì pts NOPTS/âm (gặp khi có `loudnorm` trước) → `adelay,asetpts=N/SR/TB,atrim,apad` (§3) |
| Không in kết quả `metadata=print`/`silencedetect` | đã đặt `-v error` → bỏ, dùng `-hide_banner -nostats` |
| Khung trích ra trống/xám | `-ss` đặt trước `-i` trên file ít keyframe → đặt sau `-i` |
| SFX trễ 3–5 khung | đặt `adelay` theo đầu file → trừ đỉnh/attack đo được |
| Sidechain cắt cụt nhạc ở cuối | key hết trước nhạc → pad key bằng `whole_dur` hoặc trộn `anullsrc` |
| File to lên sau alimiter | thiếu `level=disabled` |
| zsh báo `====== not found` | zsh hiểu `=word` là tìm lệnh → luôn đặt chuỗi trong nháy: `echo "====="` |
| `apad` báo `Unable to parse "whole_dur" option value ""` | zsh đọc `$DUR[c0]` là **chỉ số mảng** → viết `${DUR}[c0]` |
| loudnorm báo `Invalid chars 'inear=true'` | zsh đọc `$OFF:linear` là biến + **modifier `:l`** → viết `${OFF}:linear`. Luật: trong filtergraph mọi biến shell đều `${…}` |
| File xuất thiếu thẻ màu (`color_transfer=unknown`) | ffmpeg 9 bỏ qua `-color_trc/-color_primaries` khi khung nguồn chưa có thẻ → thêm `setparams=…` (§6) |
| Không có ảnh khung cuối | `-sseof` quá sát cuối (< 1 khung) → `-sseof -0.25` + `-update 1` |
| Tiếng "nối máy" giữa hai câu | khe là lặng số `anullsrc` → room tone từ WAV (`05-am-thanh-sfx.md` §5) |
| Mất tiếng gốc khi ghép SFX | `-map 0:v -map 1:a` bỏ hẳn âm gốc → trộn âm gốc vào đồ thị, không thay thế |
| `No such filter: 'drawtext'` | ffmpeg cài qua Homebrew không có libfreetype → bỏ nhãn chữ, giữ thứ tự khung theo danh sách mốc (hoặc ghi nhãn bằng PIL), rồi ghép bằng `tile=6x2` |
| Ghép âm master vào bản render mà không encode lại hình | `-map 0:v -map 1:a -c:v copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0 -c:a aac -b:a 192k -movflags +faststart`. Kiểm: tương quan chéo âm giao với master phải ra lệch 0 mẫu, tương quan 1,0 |
| Trắng tv 235 đổi sang RGB ra 253, không phải 255; mọi phép tính trong RGB lệch ~1 % (mất ~2 dB khi so) | swscale mặc định làm tròn nhanh → `scale=in_color_matrix=bt709:in_range=tv:flags=accurate_rnd+full_chroma_int+full_chroma_inp,format=gbrp`, chiều ra cũng thêm `flags=…` như vậy |
| Nối nhiều đoạn bằng concat rồi `psnr`/`blend` với file khác: điểm thấp đúng các lúc chuyển cảnh, ra dư 1 khung | concat làm tròn mốc thời gian từng đoạn, framesync ghép lệch khung → `setpts=N/30/TB` cho **mọi** nhánh vào trước khi so/ghép |

## 9. Tách đồ hoạ thành mẫu CapCut (Nhân + Màn hình)

Mẫu CapCut thay được clip mà vẫn giữ chữ/hiệu ứng: đường chính là các ô clip, trên đó 2 lớp phủ M (chế độ **Nhân**) và S (chế độ **Màn hình**). CapCut không có chế độ "Cộng".

- Render lớp đồ hoạ 2 lần, nền đen (B) và nền trắng (W), cùng một bản (HyperFrames: chèn CSS ẩn footage + đổi nền gốc; MP4 `--crf 10` là đủ, khỏi cần MOV alpha). Điều kiện: đồ hoạ chỉ ghép alpha thường, không `mix-blend-mode`/filter. Kiểm: W ≥ B mọi điểm.
- **S = B** (= màu × α). **M = (W − B) / (255 − B)** theo từng kênh (= (1 − α)/(1 − S)), **không** phải xám 1 − α.
  - Lý do: Màn hình(x, S) = x + S − x·S. Với x = clip × M thì kết quả = clip·M·(1 − S) + S = clip·(1 − α) + màu·α: đúng phép ghép alpha với **mọi** clip thay vào; M ≤ 1 vì màu ≤ 1.
  - M xám 1 − α làm ánh sáng bán trong suốt (bùng sáng, chớp trắng, vệt sáng) ra **xám đục** (Calokid: 62 khung < 30 dB, thấp nhất 19 dB → với M theo công thức: 0 khung, mọi khung ≥ 40 dB).
- Lệnh M: `[0:v]${IN}[w];[1:v]${IN}[b];[w][b]blend=all_expr='if(gte(B,255),255,clip(255*(A-B)/(255-B),0,255))',${OUT}` với `IN`/`OUT` là `scale=…bt709…:flags=accurate_rnd+full_chroma_int+full_chroma_inp` (§8). S: encode lại B yuv→yuv, không đổi màu.
- Ô clip: cắt từ lớp footage theo **số khung** `ceil(t·fps)` (`trim=start_frame=…:end_frame=…`), không tiếng; âm thanh mẫu ghép vào M.
- Kiểm trước khi đẩy lên điện thoại: nối các ô (concat) × M rồi `blend=all_mode=screen` với S, so `psnr` với video gốc (nhớ `setpts=N/30/TB`, §8). Mã chạy thật: Calokid `tools/tpl_prep.py`, `tools/tpl_post.py`.

