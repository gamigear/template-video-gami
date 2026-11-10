# 10 · Nguồn đã nghiên cứu (đừng nghiên cứu lại từ đầu)

Tổng hợp 16/10 – 02/11/2026. Bản phân tích đầy đủ từng nguồn (cái mượn, cái bỏ, lý do): `/Users/dteanh/Projects/Fisoft/output/reels/HOC-HOI-SKILL-VIDEO.md` (mục 1–16). Quyết định nền: **HyperFrames (render) + GSAP (chuyển động) + ffmpeg (âm thanh, ghép)**; Charlie Hills (tác giả danh sách 28 công cụ) cũng khuyên đúng cặp GSAP + HyperFrames để bắt đầu.

Ký hiệu: ✅ dùng/giữ · 🧩 chỉ mượn ý · ❌ bỏ.

## 1. Repo/skill làm video bằng code

| Nguồn | Là gì | Giấy phép | Kết luận | Ý chính đã mượn |
|---|---|---|---|---|
| heygen-com/hyperframes | HTML → video, seek timeline từng khung | Apache-2.0 | ✅ | nền tảng render; registry ~450 khối |
| AbubakrChan/product-launch-motion (v1 `legacy/`) | phim sản phẩm dẫn bằng lời trên HyperFrames | MIT (phim mẫu không dùng được) | 🧩 | 34 bẫy HyperFrames/GSAP; danh sách số được phép; kiểm SFX nghe được trong file giao; không ghi đè bản render; 3 hướng hình bỏ 2 |
| cth9191/animate | canvas 1 file, 7 phong cách vẽ | MIT | 🧩 | textcheck, dead beats, story arc, phone sheet 360 px, lặng trước điểm nhấn, ≤ 3,5 từ/s, LOG.md cảnh yếu nhất |
| whaleyxbt/claude-motion | Remotion + engine SFX Python | MIT (Remotion cần license công ty) | 🧩 | bảng số chuyển động (ease, stagger, giữ đọc), khung 0 không đen |
| howseen-ai/claude-motion-design | sổ tay kinh nghiệm | MIT | 🧩 | phim sản phẩm dạng chuỗi, ui-tokens, chống vẻ AI, agent phê bình mặc định bác bỏ, bắt khung nháy |
| lemomo-ai/lemo-opuscar | 51 phong cách + hướng dẫn đạo diễn | MIT | 🧩 | readcheck, kiểm giọng Whisper, Living Screencast |
| fx-studio/mini-video-workspace | xưởng 1 khuôn, Python + Playwright | phi thương mại | 🧩 | kiểm seek tất định 3 thứ tự, chặn mạng lúc render |
| showheyohtaki/motion-prompt | từ điển 120 tên hiệu ứng có số, Canvas 2D | MIT (giữ dòng ghi công khi chép code) | 🧩 | duyệt bằng tên + spec số; nhịp UI chuẩn; khung phẳng + khớp vòng; prompt video theo tên + spec |
| nateherkai/hyperframes-student-kit (Herk Edit Kit) | 15 skill + playbook HyperFrames + GSAP | MIT + Use Permission (brand AIS cấm) | 🧩 | con số khoảng ngừng, room tone, LUFS từng câu, validator có test đối chứng, tương phản phụ đề, ease có thời lượng, neo chống khung đen, cổng 3 giây |
| Motion Design Skill bản Việt hoá (Ngô Băng AI) ← `motion-showreel` của Herk | showreel 10–30 s cắt theo beat | kit gốc MIT; bản Việt hoá **bắt in quảng cáo mỗi phiên** | 🧩 không cài | dấu tiếng Việt bị cắt; 8 bẫy HyperFrames; strip 10 khung; pha beat dải kick |
| browser-use/video-use | cắt footage quay thật bằng transcript (ElevenLabs Scribe) + ffmpeg; **không dính trình duyệt** | MIT (Scribe trả phí) | 🧩 | ảnh ghép khung + sóng + từ tại mỗi mốc (→ `timeline_view.py`), trần 3 vòng tự sửa, sàn phụ đề 0,35 s, khẳng định font, tone-map HDR |
| charlie947/motion-graphics-skills | 15 skill lời nhắc, xuất HyperFrames | MIT | 🧩 | mổ xẻ video mẫu 5 dòng, "người lạ biết gì trước giây 4", 16 công thức hiệu ứng, soi 200 px, thông số reel-export |
| Barty-Bart/motion-graphics › `sound-effects` | luật SFX + 103 file CC0 | MIT; SFX CC0 | 🧩 | mức theo loại SFX, 5 mốc cho người nghe, đo mono; `sound_pass.py` **bỏ âm gốc video** → không dùng thẳng |
| CloudAI-X/threejs-skills | 13 SKILL.md cho three.js r186 | MIT | ✅ (cài cho riêng dự án 3D) | tra API; luật thời gian của video thắng gợi ý `setAnimationLoop` |
| greensock/GSAP + plugin | engine chuyển động | miễn phí cả thương mại (3.13+) | ✅ | CustomEase, DrawSVG, MotionPath, MorphSVG, SplitText |
| greensock/gsap-skills | skill chính thức GSAP | MIT | ❌ không cần | `04-chuyen-dong.md` + `hyperframes-animation` đã phủ |
| LottieFiles/motion-design-skill | 12 nguyên tắc Disney cho UI | MIT | 🧩 đọc nhanh | |
| anthropics/skills › `frontend-design` | chống thiết kế "mặc định AI" | theo từng skill | 🧩 | 5 cụm dấu hiệu AI |
| ahujasid/mcp-for-blender | MCP điều khiển Blender | MIT; telemetry mặc định bật (`DISABLE_TELEMETRY=true`) | 🧩 có điều kiện | xưởng làm `.glb` CC0 (Poly Haven, Poly Pizza lọc CC0) → nạp vào three.js |
| airbnb/lottie-web | hoạt hình JSON | MIT; repo gần như đứng | 🧩 tuỳ chọn | icon động qua adapter HyperFrames, ưu tiên dotLottie |
| openai/whisper (faster-whisper) | ASR | MIT | ✅ | kiểm giọng TTS so kịch bản (`--language vi`, không dùng model `.en`) |
| Remotion + remotion-dev/skills, claude-remotion-skill | React → video | Remotion License (công ty ≥ 4 người phải mua) | ❌ | |
| manim, motion-canvas, revideo | hoạt hình toán / TS editor / engine dịch vụ | MIT | ❌ | |
| anime.js, react-three-fiber, Tone.js | engine phụ | MIT | ❌ | một engine mỗi khuôn; không tổng hợp tiếng bằng code |
| shadcn, react-bits (MIT + Commons Clause), magicui, motion-primitives, motion.dev | thư viện UI web | | ❌ cho video (chỉ website) | |
| 21st-dev/magic-mcp, elevenlabs/skills, after-effects-mcp | dịch vụ trả phí / Adobe | | ❌ | |
| calesthio/OpenMontage | xưởng sản xuất video cho agent: 12 pipeline YAML + ~70 skill + ~220 công cụ bọc ~60 API (phần lớn trả phí); runtime Remotion hoặc HyperFrames | **AGPL-3.0** (chép mã vào khuôn rồi đưa người khác/chạy dịch vụ → phải mở mã) | 🧩 chỉ mượn ý, tự viết | cổng kiểm trong mã yếu hơn README (khung đen theo cỡ PNG, âm chỉ volumedetect); mượn: `check --at-transitions`, ASR báo từ chèn, sổ tín dụng, luật zoom demo màn hình, bẫy keyframe/`--workers 1`, hồ sơ khẩu vị, Kenney CC0 cho three.js, lò xo công thức đóng (Ink Theater) |
| hypit-ai/hypit | ngôn ngữ đánh dấu SVML/SVS + trình biên dịch video cho agent; thời gian neo theo từ (WhisperX); render HTML bằng nhiều Chromium; phần lớn nhà cung cấp trả phí | Apache-2.0 sửa đổi (cấm chạy dịch vụ nhiều khách; giữ tên/logo Hypit trên CLI) | 🧩 chỉ mượn ý | quảng cáo lớn hơn mã: "clone video viral" là agent tự viết ANALYSIS/TIMELINE, không có lệnh "100 biến thể", không kiểm chữ chồng/tương phản, không LUFS, không tiếng Việt; mượn: khớp kịch bản ↔ từ ASR (nhóm 4×4, phạt sót 0,5/chèn 0,35, nội suy theo số chữ), dò cắt ffmpeg 32×32 ngưỡng 0,1, lưới khung kèm lời `--around`, luật phụ đề hiện phủ trọn lời, kiểm số khung sau render, "giữ vai trò, làm lại hình thức" |
| notivn/AIEVv2 | xưởng video tiếng Việt của noti.vn cho người không biết code: Next.js + Express/Claude Agent SDK, HyperFrames dựng cảnh + Remotion ghép, 20 skill, Gemini TTS + VieNeu v3 Turbo, faster-whisper, QC tự động | MIT ở gốc; `gateways/chatgpt`, `gateways/gemini-web` AGPL (điều khiển bản web ChatGPT/Gemini) | 🧩 chỉ mượn ý | ngưỡng QC file giao (lặng đuôi 4 s cuối −45 dB > 1,2 s, `blackdetect=d=0.25:pic_th=0.98:pix_th=0.03`, `freezedetect=n=-60dB:d=2`, TP cảnh báo −1/hỏng −0,5); nhạc nền luôn fade-out 1 s cuối + thư viện nhạc gắn tag mood; phong cách 4 trường art/avoid/palette/motion; `deadWeight` dò từ đệm/vấp/lặp tất định, không cắt theo mặt chữ vì từ đệm tiếng Việt trùng từ có nghĩa; bẫy giấy phép VieNeu v2. Không dùng: gateways, công cụ xoá watermark, 86 SFX không hồ sơ giấy phép, 127 logo thương hiệu |
| kurbaitaev/ghost-editor | skill Claude Code dựng reel talking-head từ bản quay thô (chọn take, theo dõi mặt, `reel.json` → HyperFrames 0.8.159, tờ duyệt, QA); 18 style dựng sẵn | MIT (clip demo của tác giả không dùng lại; SFX/nhạc Mixkit tải về) | 🧩 (chạy thử 10/11/2026 ở `capcut/research/ghost-editor-test`) | mốc clip floor theo lưới khung (07 §9), SFX đo so với giọng trên bản tách riêng (05 §11), tờ duyệt khung (01 §8), chọn take + đặt chữ quanh mặt (06 §10), nền giữ khung cuối (06 §9). Không thay khuôn: font thiếu dấu tiếng Việt, chip đo theo font Latin, chỉ hỗ trợ ElevenLabs, render chạy tại chỗ, lỗi symlink khi đặt ngoài `~/.claude/skills` |
| EditAtlas/skills (commit `f7b9505`, 10/11/2026) | 3 skill Claude Code dựa trên thư viện edit.trysometh.ing (kỹ thuật có slug, template, SFX; MCP hoặc REST `/api/v1/techniques`, `/api/v1/sfx`): `sound-design`, `transcribe` (faster-whisper, mốc từng từ), `video-breakdown` (mổ xẻ reel mẫu); có `description_vi` và ca test tiếng Việt; beta | Apache-2.0 (tên/logo không cấp phép); **thư viện SFX đi kèm không rõ giấy phép** (§3) | 🧩 (chạy thử `video-breakdown` 10/11/2026, `capcut/research/editatlas-skills`) | công cụ mổ xẻ reel mẫu đo mối nối/camera/chữ/timing (01 §2); thiết lập Whisper đo trên tiếng Việt: VAD 500 ms, không hotword, lượt hai (03 §4); nhịp SFX theo loại phim + kiểm sync bằng định vị lại dạng sóng (05 §2, §8); timing motion design đo trên demo (04 §1). Không dùng: tải SFX của họ, cài nguyên plugin cho dự án giao khách |
| flaviorg/motion-studio | brief → chụp brand → lưới beat → phê bình chấm điểm → MP4 (HyperFrames) | ? | ⏳ chưa xem | ứng viên đọc tiếp |

## 2. Công cụ phim AI và dựng tay

| Nguồn | Kết luận | Lý do |
|---|---|---|
| Google Flow · Omni 1.1 Flash (10 s, khung đầu/cuối, 9:16, 720p) | ✅ | model duy nhất ra 10 s; Veo 3.1 tối đa 8 s; khung đầu/cuối chỉ trên web |
| Muse AI, ChatGPT GPT Image, Codex CLI `image_generation` | ✅ | ảnh nhân vật, bối cảnh, khung đầu/cuối hàng loạt (Codex cần `stdin=/dev/null`) |
| Gami Studio (Gami Flow Queue, tiện ích Chrome) | 🧩 | hàng đợi nhiều clip trên một tab Flow; chưa có cổng khung cuối |
| crisng95/FlowKit | ❌ | **vượt lớp chống bot reCAPTCHA của Google** (`hijack_bypass.js`) → nguy cơ khoá tài khoản, trái điều khoản. Chỉ mượn ý: chấm clip bằng ảnh ghép khung, `Negative: subtitles, watermark, text overlay`, không gửi lại lệnh khi hết giờ chờ |
| muse2api | ❌ | lái muse.ai bằng cookie |
| jub0t/Concat (trình dựng Rust, MCP) | 🧩 phương án sửa tay | AGPL-3.0, beta; TTS không có tiếng Việt; lỗi chuỗi chuyển cảnh đè track |
| ComfyUI (thư viện gonghaosnail.com, ~50 skill ClawHub) | ❌ trên máy hiện có | M1 Pro 16 GB phải GGUF, chậm; LTX-2.3 cần GPU ≥ 24 GB VRAM, ~1 giờ/clip. Mượn: thẻ phong cách 5 phần, bộ 4 ảnh vàng, cổng tiền kiểm, prompt JSON có cấu trúc |

## 3. Âm thanh

| Nguồn | Kết luận |
|---|---|
| Reel Quạ HD "Cách chèn Sound Effects" | 🧩 hook bằng tiếng cao chói; ≤ 1 tiếng căng/7 s; "nghe bắt tai là được" |
| Bộ "BASIC SFX QUẠ HD" (Drive, 1.310 file) | chỉ dùng phần Mister Horse Free + 効果音ラボ (và phải tự tải lại từ trang gốc); QUẠ BASIC/Anime/SUSPEND ALERT là meme/Epidemic/Storyblocks → ❌ |
| Mister Horse Free, 効果音ラボ, Kenney/Freesound CC0, Mixkit Free, HeyGen (`/media-use`) | ✅ nguồn được phép |
| EditAtlas/sfx (2.302 file, 775 MB, mirror GitHub của edit.trysometh.ing) | ❌ cho bản giao (kiểm 10/11/2026): repo không có LICENSE, bản ghi API không có trường nguồn/giấy phép; ~900 mã `sfx-mi…`, ~50 mã `sfx-fs…` (đoán là Mixkit/Freesound, **chưa xác minh**; nếu là Mixkit thì việc phát tán lại trái điều khoản Mixkit). Chỉ dùng mô tả + số đo của họ để tham khảo cách chọn tiếng |

## 4. Giọng đọc

| Nguồn | Kết luận |
|---|---|
| VieNeu TTS (chạy máy, server `127.0.0.1:23334`, nhân bản giọng trong app VieNeuTTS) | ✅ tiếng Việt; từng câu một file WAV; giọng nhân bản chỉ nạp khi server khởi động |
| Kokoro, Chatterbox, Qwen3-TTS, OmniVoice, ElevenLabs | ❌ cho tiếng Việt (không có hoặc trả phí) |
| Omni tự nói thoại tiếng Việt trong clip | ⚠️ dùng được nhưng hay lặp câu/vấp/thêm câu → kiểm từng clip, cắt ở hậu kỳ |

## 5. Cách thêm nguồn mới

1. So với bảng trên và `HOC-HOI-SKILL-VIDEO.md`; chỉ ghi điểm **mới**.
2. Ghi: là gì, giấy phép, phụ thuộc trả phí, cái mượn (có con số), cái bỏ + lý do.
3. Quy tắc mượn: chỉ lấy **tên, con số, cách kiểm**; không chép code nếu giấy phép không rõ; không cài skill bắt in quảng cáo hoặc gọi dịch vụ trả phí ngầm.
4. Cập nhật file tham chiếu tương ứng trong sổ tay này.
