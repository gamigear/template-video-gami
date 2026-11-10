#!/bin/sh
# Tải lại 14 clip Pexels dùng cho bản demo (giấy phép Pexels không cho đăng lại nguyên bản lên kho khác,
# nên repo chỉ giữ danh sách nguồn trong credits.tsv). Chạy: sh travel_cinematic/stock/download_stock.sh
cd "$(dirname "$0")" || exit 1
tail -n +2 credits.tsv | while IFS="$(printf '\t')" read -r n id author title url; do
  [ -f "clip_$n.mp4" ] || curl -L --fail -o "clip_$n.mp4" "$url"
done
