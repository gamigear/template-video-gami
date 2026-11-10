# Gallery: cách dựng GIF xem trước

| File | Nguồn | Kích thước |
|---|---|---|
| `gallery.gif` | lưới tổng: mỗi template một thẻ, chạy cùng lúc (`make_gallery_gif.py`) | 994×348, 8 fps |
| `spotlight_916.gif` | `npx hyperframes snapshot` (khung thật của HyperFrames) | 270×480, 12 fps |
| `travel_cinematic.gif`, `welcome_travel.gif` | `capcut_anim.py` (dựng gần đúng từ `draft_info.json`) | 384×216, 8 fps |
| `*.jpg` | dải khung hình tĩnh (`make_capcut_preview.py`, snapshot) | |

Không cần render MP4. Mọi bước chạy trên máy đang có dự án.

## 1. Khung hình từng template

```bash
# HyperFrames: 139 khung đều nhau trong 11,5 s (≈ 12 fps)
cd spotlight_916 && npx hyperframes snapshot --range 0,11.5 --frames 139 -o /tmp/gif_spot && cd ..
# tên gốc frame-100 đứng trước frame-11 khi sắp theo chữ: đổi tên theo thứ tự thời gian
mkdir -p /tmp/gif_spot_seq && ls /tmp/gif_spot/frame-*.png | sed -E 's/.*-at-([0-9.]+)s\.png/\1 &/' | sort -n \
  | awk '{printf "cp %s /tmp/gif_spot_seq/f%04d.png\n",$2,NR-1}' | sh

# CapCut: draft phải nằm trong thư mục draft của CapCut (~2 phút mỗi draft)
python3 gallery/capcut_anim.py "Travel Cinematic Demo v3" /tmp/gif_tc
python3 gallery/capcut_anim.py "Welcome Travel Moment Demo" /tmp/gif_wt
```

`capcut_anim.py` cần `numpy`, `pillow` và `ffmpeg`. Nó lấy khung clip theo thời gian và vẽ mask chữ nhật, fade vào/ra,
cùng vài hiệu ứng gần đúng: 闭幕 (khép màn), 渐隐闭幕 (mờ về đen), 胶片漏光 (loé sáng phim), 闪白 (loé trắng),
青橙 (teal–cam). Font CapCut được thay bằng font hệ thống, nên chữ chỉ đúng vị trí và cỡ, không đúng mặt chữ.

## 2. GIF lẻ

```bash
ffmpeg -framerate 12.087 -i /tmp/gif_spot_seq/f%04d.png -vf "scale=270:480:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle" -loop 0 gallery/spotlight_916.gif
ffmpeg -framerate 10 -i /tmp/gif_tc/f%04d.png -vf "fps=8,scale=384:216:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" -loop 0 gallery/travel_cinematic.gif
```

## 3. Lưới tổng

Thêm template: thêm một dòng vào `CARDS` trong `make_gallery_gif.py` (tên, dòng phụ, màu chấm, thư mục khung, fps,
tỉ lệ). Template ngắn hơn sẽ lặp lại cho tới khi template dài nhất chạy hết.

```bash
python3 gallery/make_gallery_gif.py /tmp/gif_grid gallery/gallery.gif
```

Giữ mỗi GIF dưới khoảng 8 MB: giảm `CARD_H`, `FPS` hoặc `max_colors` nếu nặng hơn.
