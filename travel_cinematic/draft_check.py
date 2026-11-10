"""Kiểm tra draft CapCut 9.5 macOS vừa sinh (chỉ đọc, không sửa gì).

Gồm hai phần:
  1. Kiểm tra riêng cho cách ghi draft của `write_draft()`: bản gốc và bản trong Timelines/ phải giống hệt,
     media phải tồn tại và nằm trong ~/Movies (sandbox), draft phải có trong root_meta_info.json.
  2. `capcut lint` + `capcut diagnose` của capcut-cli (https://github.com/renezander030/capcut-cli),
     đã lọc các cảnh báo không đúng với draft của mình (xem IGNORED).

Dùng riêng:
    .venv/bin/python travel_cinematic/draft_check.py "QUAHD Doc 9x16" "Travel Cinematic Demo v3"
    .venv/bin/python travel_cinematic/draft_check.py --strict <thư mục draft>   # có lỗi thì thoát mã 1

capcut-cli được tìm theo thứ tự: biến môi trường CAPCUT_CLI, tools/capcut-cli trong project, `capcut` trên PATH.
Không tìm thấy thì chỉ chạy phần 1.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

DRAFT_ROOT = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
MOVIES = os.path.realpath(os.path.expanduser("~/Movies"))
HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_CLI = os.path.join(HERE, "..", "tools", "capcut-cli", "node_modules", ".bin", "capcut")

# Mã lint của capcut-cli không đúng với draft do write_draft() sinh trên CapCut 9.5 Mac
IGNORED = {
    "media-outside-draft": "media để ở ~/Movies/CapCut/Template Media vẫn mở tốt trên 9.5 (đã kiểm tra riêng ở phần 1)",
    "media-unlinked": "draft Travel Cinematic Demo/v2 không có local_material_id vẫn liên kết được trên 9.5",
    "media-unregistered": "như trên: draft_materials rỗng không làm mất media trên 9.5",
    "keyframe-trimmed-clock": "chỉ áp dụng cho Jianying Pro 11.6",
}


def find_cli():
    for c in (os.environ.get("CAPCUT_CLI"), LOCAL_CLI, shutil.which("capcut")):
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return os.path.abspath(c)
    return None


def run_cli(cli, *args):
    """Chạy một lệnh chỉ đọc của capcut-cli, trả về JSON (lint thoát mã 1 khi có cảnh báo nên không xét mã thoát)."""
    # stdout ghi ra file tạm chứ không qua pipe: Node cắt output qua pipe ở 64 KB khi thoát, draft nhiều đoạn
    # (vd. Welcome Travel Moment, ~108 KB) sẽ ra JSON cụt
    with tempfile.TemporaryFile("w+", encoding="utf-8") as out:
        r = subprocess.run([cli, *args], stdout=out, stderr=subprocess.PIPE, text=True, timeout=180)
        out.seek(0)
        stdout = out.read()
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"capcut {args[0]} không trả JSON: {(r.stderr or stdout).strip()[:300]}")


def own_checks(folder):
    """Kiểm tra cấu trúc mà write_draft() ghi ra. Trả về (draft, [(mức, mã, nội dung)])."""
    issues = []
    root_path = os.path.join(folder, "draft_info.json")
    with open(root_path, "rb") as f:
        root_bytes = f.read()
    draft = json.loads(root_bytes)

    # Timelines/: CapCut 9.x đọc bản lồng bên trong, bản gốc chỉ là bản sao
    try:
        with open(os.path.join(folder, "Timelines", "project.json"), encoding="utf-8") as f:
            main_id = json.load(f)["main_timeline_id"]
        nested = os.path.join(folder, "Timelines", main_id, "draft_info.json")
        if not os.path.exists(nested):
            issues.append(("error", "timeline-missing", f"thiếu Timelines/{main_id}/draft_info.json"))
        else:
            with open(nested, "rb") as f:
                if f.read() != root_bytes:
                    issues.append(("error", "timeline-diverged",
                                   "Timelines/<id>/draft_info.json khác bản gốc — CapCut sẽ đọc bản trong Timelines/"))
        if draft.get("id") != main_id:
            issues.append(("error", "timeline-id", f"id của draft ({draft.get('id')}) khác main_timeline_id ({main_id})"))
    except (OSError, KeyError, json.JSONDecodeError) as e:
        issues.append(("error", "timeline-project", f"không đọc được Timelines/project.json: {e}"))

    # Media: phải tồn tại và nằm trong ~/Movies, nếu không CapCut (sandbox App Store) báo chưa liên kết
    seen = set()
    for kind in ("videos", "audios"):
        for m in draft.get("materials", {}).get(kind, []):
            p = m.get("path")
            if not p or p in seen or m.get("type") in ("text", "color"):
                continue
            seen.add(p)
            if not os.path.exists(p):
                issues.append(("error", "media-missing", f"không có file: {p}"))
            elif not os.path.realpath(p).startswith(MOVIES + os.sep):
                issues.append(("error", "media-sandbox", f"media nằm ngoài ~/Movies, CapCut không đọc được: {p}"))

    # Đăng ký trong root_meta_info.json, nếu không CapCut không hiện draft
    store = os.path.dirname(os.path.abspath(folder))
    try:
        with open(os.path.join(store, "root_meta_info.json"), encoding="utf-8") as f:
            entries = json.load(f).get("all_draft_store", [])
        if not any(os.path.abspath(e.get("draft_fold_path", "")) == os.path.abspath(folder) for e in entries):
            issues.append(("error", "not-registered", "draft chưa có trong root_meta_info.json, CapCut sẽ không hiện"))
    except (OSError, json.JSONDecodeError) as e:
        issues.append(("warning", "registry", f"không đọc được root_meta_info.json: {e}"))
    return draft, issues


def cli_checks(cli, folder, draft):
    issues = []
    diag = run_cli(cli, "diagnose", folder)
    if diag.get("editor_running"):
        issues.append(("warning", "editor-running", "CapCut đang mở — đóng CapCut trước khi sinh draft"))
    if diag.get("diverged"):
        issues.append(("error", "diverged", "các file timeline trong draft không khớp nhau"))
    if diag.get("write_guard") not in (None, "ok"):
        issues.append(("warning", "write-guard", f"phiên bản ngoài vùng an toàn của capcut-cli: {diag.get('version')}"))

    ignored = dict(IGNORED)
    if draft.get("config", {}).get("maintrack_adsorb") is False:
        ignored["main-track-gap"] = "đã tắt nam châm track chính (maintrack_adsorb=False)"
    # pyCapCut gắn id speed vào mọi segment (segment.py) nhưng không xuất material speed cho text;
    # CapCut tự bỏ ref thừa này khi lưu, nên chỉ bỏ qua trên text segment
    text_segs = {s["id"] for t in draft.get("tracks", []) if t.get("type") == "text" for s in t.get("segments", [])}
    skipped = {}
    for it in run_cli(cli, "lint", folder).get("issues", []):
        code = it.get("code", "?")
        if code == "dangling-companion-ref" and it.get("location", {}).get("segment_id") in text_segs:
            code = "dangling-companion-ref(text)"
            skipped[code] = skipped.get(code, 0) + 1
            continue
        if code in ignored:
            skipped[code] = skipped.get(code, 0) + 1
            continue
        issues.append((it.get("severity", "info"), code, it.get("message", "")))
    return issues, skipped


def check_draft(folder, strict=False, quiet_info=True):
    """In kết quả kiểm tra; trả về danh sách lỗi/cảnh báo. strict=True thì có lỗi sẽ thoát chương trình."""
    folder = os.path.abspath(folder)
    print(f"\nKiểm tra draft: {folder}")
    draft, issues = own_checks(folder)
    skipped = {}
    cli = find_cli()
    if cli:
        try:
            more, skipped = cli_checks(cli, folder, draft)
            issues += more
        except (RuntimeError, OSError, subprocess.TimeoutExpired) as e:
            issues.append(("warning", "capcut-cli", f"không chạy được capcut-cli: {e}"))
    else:
        print("  (không tìm thấy capcut-cli — chỉ kiểm tra cấu trúc; cài: npm install --prefix tools/capcut-cli "
              "--ignore-scripts --save-exact capcut-cli@0.31.1)")

    rank = {"error": 0, "warning": 1, "info": 2}
    issues.sort(key=lambda i: rank.get(i[0], 3))
    shown = [i for i in issues if not (quiet_info and i[0] == "info")]
    for sev, code, msg in shown:
        print(f"  {sev.upper():7} {code:24} {msg}")
    n_err = sum(i[0] == "error" for i in issues)
    n_warn = sum(i[0] == "warning" for i in issues)
    n_info = len(issues) - n_err - n_warn
    tail = ", bỏ qua: " +", ".join(f"{k}×{v}" for k, v in sorted(skipped.items())) if skipped else ""
    hidden = f" (ẩn {n_info} info)" if quiet_info and n_info else ""
    print(f"  → {n_err} lỗi, {n_warn} cảnh báo, {n_info} info{hidden}{tail}")
    if strict and n_err:
        raise SystemExit(f"Draft có {n_err} lỗi: {folder}")
    return [i for i in issues if i[0] in ("error", "warning")]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("drafts", nargs="+", help="thư mục draft hoặc tên draft trong kho CapCut")
    ap.add_argument("--strict", action="store_true", help="thoát mã 1 nếu có lỗi")
    ap.add_argument("--info", action="store_true", help="hiện cả mục info")
    a = ap.parse_args()
    failed = False
    for d in a.drafts:
        folder = d if os.path.isdir(d) else os.path.join(DRAFT_ROOT, d)
        problems = check_draft(folder, quiet_info=not a.info)
        failed |= any(p[0] == "error" for p in problems)
    sys.exit(1 if a.strict and failed else 0)


if __name__ == "__main__":
    main()
