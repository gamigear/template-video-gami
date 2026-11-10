# Nghiên cứu CapCut & phương án tạo template

_Ngày: 2026-10-22 · Máy khảo sát: macOS, CapCut Desktop 9.5.0 (`com.lemon.lvoverseas`)_

## 1. Phân tích định dạng draft trên máy (đã kiểm chứng)

### 1.1 Vị trí & cấu trúc thư mục

```
~/Movies/CapCut/User Data/Projects/
├── com.lveditor.draft/                 # draft thường
│   ├── root_meta_info.json             # "sổ đăng ký" tất cả draft (CapCut đọc để hiện danh sách)
│   └── <tên draft>/
│       ├── draft_info.json             # TIMELINE CHÍNH (tracks + materials)
│       ├── draft_info.json.bak
│       ├── draft_meta_info.json        # metadata: id, tên, đường dẫn, thời lượng, cover
│       ├── draft_cover.jpg
│       ├── Timelines/project.json      # danh sách timeline (multi-timeline), main_timeline_id
│       ├── Timelines/<timeline-id>/    # bản sao draft_info.json theo từng timeline
│       ├── key_value.json, attachment_*.json, draft_agency_config.json ...
│       └── Resources/, matting/, smart_crop/, adjust_mask/ ...
├── com.lveditor.textTemplate.draft/    # preset text template
└── com.lveditor.cloud.draft_<uid>/     # draft đồng bộ cloud
```

### 1.2 Phát hiện quan trọng: draft KHÔNG bị mã hoá ở bản 9.5.0 (macOS)

- `draft_info.json` của cả 3 draft (`0926`, `1007`, `CHINSU Chan Tron Ngang 123s`) đều là **JSON thuần**.
  `file` nhận diện là `JSON data`, `json.load` đọc được trực tiếp.
- Schema version: `"version": 360000`, `"new_version": "187.0.0"`, `platform.app_version: "9.5.0"`, `os: "mac"`.
- Vì vậy có thể **đọc, sửa và sinh draft bằng code** trên máy này. Lưu ý: CapCut có thể bật mã hoá ở bản sau,
  nên cần **khoá phiên bản CapCut** (tắt auto-update) nếu đi theo hướng này.

### 1.3 Mô hình dữ liệu `draft_info.json`

| Thành phần | Ý nghĩa | Ví dụ thực tế (draft `1007`) |
|---|---|---|
| `canvas_config` | Kích thước khung | 1080×1920 (dọc), fps 30 |
| `duration` | Thời lượng, **đơn vị micro-giây** | 54 633 333 µs ≈ 54,6 s |
| `tracks[]` | Các track: `video`, `audio`, `text`, `effect`, `filter`, `sticker`… | 1 video, 1 text (24 segment), 1 audio |
| `tracks[].segments[]` | Clip trên timeline: `material_id`, `target_timerange` (vị trí trên timeline), `source_timerange` (đoạn cắt từ nguồn), `clip` (scale/rotation/transform/flip/alpha), `speed`, `volume`, `extra_material_refs` | |
| `materials.*` | Kho tài nguyên, segment tham chiếu bằng UUID | `videos`(1), `texts`(24), `text_templates`(24), `material_animations`(25), `speeds`, `canvases`, `beats`, `placeholder_infos`, `vocal_separations`… |
| `materials.videos[].path` | **Đường dẫn tuyệt đối** tới file media | `/Users/<tên>/Downloads/ong-canh3-goc-da-final.mp4` |
| `materials.texts[].content` | Chuỗi JSON lồng: `text` + `styles[]` (fill, stroke, shadow, font, range) | `"gặp ai cũng kể chuyện đời mình"` |
| `materials.text_templates[]` | Hiệu ứng chữ tải từ store, có `effect_id`/`resource_id` + đường dẫn cache | `变色放大综艺体` (id 7535365128418594064) |
| `keyframes`, `keyframe_graph_list` | Keyframe animation | |
| `platform` | Thông tin thiết bị (`device_id`, `hard_disk_id`, `mac_address` dạng hash) | |

Quan hệ: **segment → `material_id` → material**; các material phụ (speed, canvas, animation, placeholder,
sound_channel_mapping, vocal_separation…) gắn qua `extra_material_refs`. Mỗi video segment trong file mẫu có
khoảng 7 ref phụ. Thiếu ref có thể làm CapCut báo lỗi hoặc bỏ qua clip.

### 1.4 Hệ quả cho việc "template hoá"

1. **Thay nội dung** (đổi video, ảnh, chữ, nhạc) chỉ cần sửa `materials.*.path` và `texts[].content`,
   rồi cập nhật `duration`, `width`/`height` và các `timerange`. Đây là cách dễ và ổn định nhất.
2. **Draft mới phải được đăng ký** trong `root_meta_info.json` (`all_draft_store[]`, `draft_ids`). Nếu không,
   CapCut không hiện draft trong danh sách. Cách an toàn: nhân bản thư mục draft mẫu, đổi `id` (UUID) ở
   `draft_info.json`, `draft_meta_info.json`, `Timelines/`, rồi thêm entry vào `root_meta_info.json`.
   **Phải đóng CapCut** khi ghi, vì CapCut ghi đè file này lúc chạy.
   **Ghi cả 2 bản:** `draft_info.json` ở gốc và `Timelines/<timeline-id>/draft_info.json`. Hai file này đang
   giống hệt nhau (đã kiểm tra bằng `cmp` với draft `1007`). Các bản CapCut mới đọc timeline từ thư mục
   `Timelines/`, nên nếu chỉ sửa file gốc thì thay đổi có thể không có tác dụng.
3. **Hiệu ứng, text template, transition và filter từ store** được tham chiếu bằng `effect_id`/`resource_id`
   cộng đường dẫn cache (`~/Library/Containers/com.lemon.lvoverseas/.../Cache/effect/<id>/...`). Khi dựng
   draft bằng code, nên **sao chép block material từ một draft đã dùng hiệu ứng đó** thay vì tự viết. Nếu cache
   chưa có, CapCut thường tự tải lại khi mở.
4. **Xuất video vẫn phải qua CapCut** (render thủ công, hoặc tự động hoá UI). Draft JSON không tự render
   được ngoài CapCut.
5. Đây là **draft dự án**, không phải "CapCut Template" công khai (template có link "Dùng mẫu" trên
   CapCut/TikTok). Template công khai phải tạo và đăng qua chức năng chính thức của CapCut (xem mục 2).

## 2. Template chính thức của CapCut

> Nguồn tra cứu đến 22/10/2026. CapCut thay đổi chính sách thường xuyên, nên mở link để kiểm tra lại.

### 2.1 Ai được đăng template
- Chỉ **creator đã được duyệt** mới đăng được. Dấu hiệu: tab **Me** trong app có mục **Creator Center**. Khi đó
  đăng bằng *Dự án mới → Post → Publish as Template*.
  ([CapCut Help, 01/2026](https://www.capcut.com/help/how-to-create-templates-in-capcut))
- Có phân hạng theo level: Lv1–2 *Exclusive Explorer*, Lv3–4 *Emerging*, Lv5+ *Elite*.
  ([trang partner US](https://www.capcut.com/partners/template-creator-us))
- **Việt Nam:** CapCut không công bố danh sách quốc gia, nhưng nhiều hướng dẫn tiếng Việt cho thấy đăng ký được
  ngay trong app: tab **Mẫu** → banner **Đăng ký** → **Tham gia ngay** → điền form Creator. CapCut cũng từng giới
  thiệu creator Việt trong chuỗi bài "CapCut Creators · Asia".
  ([didongviet](https://didongviet.vn/dchannel/cach-dang-video-len-capcut/),
  [dienmaycholon](https://dienmaycholon.com/kien-thuc/cach-dang-mau-capcut))
- Điều kiện (theo nguồn bên thứ ba): **đủ 18 tuổi**, đăng ký cá nhân (không phải brand/agency), không yêu cầu
  số follower tối thiểu. Nên chuẩn bị sẵn vài bản edit gốc.

### 2.2 Clip thay thế (replaceable) – điểm mấu chốt
| Nền tảng | Đánh dấu clip thay thế | Đăng template |
|---|---|---|
| **Mobile** | Có (*Post as Template → Confirm editable clips*) | Có |
| **Web** (capcut.com) | Có (*Share → Share as Template → Set Replaceable Clips*, giới hạn thời lượng, chọn ảnh hoặc video) | Có |
| **Desktop** (Win/Mac 9.x) | **Không** | **Không**, chỉ dùng template có sẵn |

→ Quy trình chính thức: **dựng trên Desktop** → đồng bộ **cloud draft** → **đánh dấu clip và đăng từ Mobile/Web**.
([CapCut Help](https://www.capcut.com/help/how-to-set-replaceable-material-clips))

### 2.3 Phân phối & kiếm tiền
- Khi xuất video dùng template rồi share thẳng lên TikTok, video có nhãn **"CapCut · Try this template"**.
  Người xem bấm vào để mở template trong CapCut (chỉ trên mobile). Link có dạng `capcut.com/template-detail/<id>`.
- Creator nhận **tiền theo lượt dùng/xuất template**, cộng thưởng từ thử thách và giới thiệu. CapCut **không công bố
  mức cụ thể**. Các con số đang lan truyền (ví dụ "300 USD/tuần") chỉ là kinh nghiệm cá nhân, và không phải khu vực
  nào cũng rút được tiền mặt.

### 2.4 API chính thức
- **Không có API công khai** để tạo hoặc sửa template hay draft CapCut.
- Gần nhất có:
  - **Pippit** (tên mới của Commerce Pro): template e-commerce, edit hàng loạt, nhưng không có API.
  - **CapCut × Codex plugin** (khoảng 09/2026): agent tạo cloud draft, tìm template, thay media.
  - **BytePlus ModelArk**: API cho mô hình sinh video Seedance (tạo video bằng AI, không phải template).

## 3. Công cụ mã nguồn mở sinh draft bằng code

| Dự án | ⭐ | Hỗ trợ | Ghi chú |
|---|---|---|---|
| **[pyCapCut](https://github.com/GuanYixuan/pyCapCut)** (`pip install pycapcut`) | ~0.7k | **CapCut quốc tế**, đã kiểm thử 8.2 & **9.5.0** | Video/ảnh/audio/text/sticker/keyframe/mask/transition/effect/filter, nhập SRT. **Template mode**: thay media và text theo tên trong draft mẫu. Phải xuất video thủ công. Nên ghim phiên bản `pycapcut==0.0.4`, vì bản 0.1.0 sẽ đổi API track. **Phù hợp nhất với máy bạn.** |
| [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) | ~4.6k | Chỉ JianYing (剪映) | Bản "gốc" của pyCapCut. Tài liệu và cộng đồng lớn nhất. |
| [VectCutAPI](https://github.com/sun-guannan/VectCutAPI) (tên cũ CapCutAPI) | ~2.3k | JianYing + CapCut | HTTP server + **MCP server** dựa trên pyJianYingDraft. Có dịch vụ render cloud trả phí. Hợp nếu muốn gọi qua API hoặc AI agent. |
| [capcut-mate](https://github.com/Hommy-master/capcut-mate) | ~2.0k | Thiên về JianYing | FastAPI/Docker, plugin Coze/n8n. |
| [capcut-cli](https://github.com/renezander030/capcut-cli) (npm) | ~0.9k | CapCut + JianYing | Sửa draft có sẵn: phụ đề, tốc độ, âm lượng, cắt video dài thành shorts. Phát hiện mã hoá nhưng không giải mã. Ghi chú theo từng phiên bản rất tốt. |
| MCP nhỏ (JmsLdrn/capcut-mcp, Atx-Guy/capcut-mcp-server…) | <100 | CapCut | Thử nghiệm, ít bảo trì. |

**Mã hoá theo phiên bản:**
- JianYing ≥ 6.0 mã hoá draft.
- CapCut quốc tế 6.x–9.x vẫn là JSON thường. Máy bạn (9.5.0) đã xác nhận điều này.
- Các bản mã hoá vẫn **mở được** draft JSON thường do tool sinh ra, nhưng sau khi app lưu lại thì không đọc ngược
  được nữa. Nguyên tắc: **chỉ sinh draft mới, không sửa đi sửa lại cùng một draft**.
- Không tool nào tự động bấm xuất video trên CapCut quốc tế.

## 4. Giải pháp thay thế (render hoàn toàn tự động, không cần CapCut)

| Công cụ | Kiểu | Chi phí | Khi nào chọn |
|---|---|---|---|
| **Remotion** | React → MP4 | Miễn phí cho cá nhân hoặc công ty ≤3 người | Dev React, cần render server hàng loạt |
| **HyperFrames** | HTML/CSS/GSAP → MP4 | Miễn phí (Apache-2.0) | Hợp làm cùng AI agent, motion graphics |
| **Shotstack / Creatomate / JSON2Video** | API JSON/cloud | ~17–54 USD/tháng trở lên | Không muốn tự vận hành hạ tầng render |
| **FFmpeg** | CLI | Miễn phí | Ghép, cắt, chèn chữ đơn giản |

Đánh đổi: các công cụ này render tự động 100% và bạn sở hữu output. Đổi lại **không có kho hiệu ứng của CapCut,
không có nhãn "Use template" trên TikTok, không có tiền thưởng template**.

## 5. Rủi ro pháp lý / điều khoản

- Điều khoản CapCut **cấm reverse engineer** dịch vụ, *"bao gồm files"*, và cấm script tự động
  ([ToS](https://www.capcut.com/clause/terms-of-service), [Material License](https://www.capcut.com/clause/material-license-agreement)).
- Mức rủi ro theo từng việc:
  - **Sinh draft JSON thường rồi tự mở trong CapCut:** vùng xám, được dùng phổ biến, rủi ro thực tế thấp.
  - **Giải mã draft JianYing ≥ 6:** rủi ro cao hơn rõ rệt (vượt qua biện pháp bảo vệ). Nên tránh.
  - **Hậu quả có thể gặp:** khoá tài khoản hoặc bị loại khỏi chương trình creator, và format draft thay đổi sau mỗi
    lần cập nhật. Khả năng bị kiện thấp.
- Hiệu ứng hoặc nhạc **Pro** trong draft vẫn cần gói Pro để xuất. Template đăng công khai phải dùng nhạc có bản quyền
  hợp lệ và nội dung gốc.

## 6. So sánh phương án & đề xuất

| Phương án | Tự động hoá | Dùng hiệu ứng CapCut | Kiếm tiền template | Độ ổn định | Rủi ro ToS |
|---|---|---|---|---|---|
| **A. Thủ công chính thức**: dựng trên Desktop, đăng từ Mobile/Web | Thấp | ✅ | ✅ | Cao | Không |
| **B. Sinh draft bằng code** (pyCapCut) từ draft mẫu, xuất video thủ công | Trung bình–cao (khâu dựng) | ✅ | ❌ (đăng template vẫn phải làm tay) | Trung bình, phụ thuộc phiên bản | Thấp–vừa |
| **C. Lai A + B**: code sinh hàng loạt biến thể → chọn bản tốt → đăng template chính thức | Cao | ✅ | ✅ | Trung bình | Thấp–vừa |
| **D. Bỏ CapCut**: Remotion/HyperFrames/Shotstack | Rất cao (cả render) | ❌ | ❌ | Cao | Không |

### Khuyến nghị
1. **Mục tiêu là template kiếm tiền trên CapCut/TikTok → phương án C.**
   - **Bước 1:** đăng ký Creator Program ngay trên app mobile (tab Mẫu → Đăng ký). Đây là điều kiện tiên quyết,
     không thể làm bằng code.
   - **Bước 2:** dựng 1–2 *draft mẫu* trên Desktop. Đặt tên rõ ràng cho clip và text cần thay (ví dụ `__VIDEO_1__`,
     `__TITLE__`).
   - **Bước 3:** viết script Python (pyCapCut, template mode) đọc CSV/Excel để sinh hàng loạt draft. Đóng CapCut
     khi chạy script và đăng ký draft vào `root_meta_info.json`.
   - **Bước 4:** mở CapCut, kiểm tra, xuất video. Bản nào đạt thì đồng bộ cloud rồi đăng template từ Mobile/Web
     và đánh dấu clip thay thế.
2. **Mục tiêu là sản xuất video quảng cáo hàng loạt** (ví dụ các video CHINSU) **mà không cần template công khai**
   → phương án B nếu cần hiệu ứng CapCut, phương án D nếu cần render tự động hoàn toàn trên server.
3. **Phòng thủ kỹ thuật:**
   - Tắt auto-update CapCut ở 9.5.0.
   - Backup `root_meta_info.json` trước khi chạy script.
   - Kiểm tra lại định dạng mỗi khi nâng cấp CapCut.

### Bước tiếp theo có thể làm ngay
Dựng một PoC nhỏ: lấy draft `CHINSU Chan Tron Ngang 123s` làm mẫu, rồi viết script nhân bản và thay 3 video cùng
nhạc nền để sinh N draft mới. Sau đó kiểm tra xem CapCut 9.5.0 có mở được không.
