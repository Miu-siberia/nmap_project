#!/usr/bin/env python3
"""ĐT-02 · alert.py — gửi cảnh báo khi diff phát hiện thay đổi.

Đọc diff.json; nếu có thay đổi thì ghi file cảnh báo và (tùy chọn) gửi Telegram.
Cấu hình qua biến môi trường (không ghi token vào repo):
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

Ví dụ:
  python3 alert.py --diff inventory/diff.json
"""
import argparse, json, os, sys, urllib.parse, urllib.request
from datetime import datetime


def build_message(d):
    lines = [f"⚠️ [ĐT-02] Phát hiện thay đổi bề mặt tấn công — {datetime.now():%Y-%m-%d %H:%M}"]
    for r in d.get("added", []):
        lines.append(f"+ MỚI {r['ip']}:{r['port']} {r.get('service','')} "
                     f"(risk={r.get('risk','?')})")
    for r in d.get("removed", []):
        lines.append(f"- MẤT {r['ip']}:{r['port']} {r.get('service','')}")
    for r in d.get("changed", []):
        lines.append(f"~ ĐỔI {r['ip']}:{r['port']} {r.get('service','')} "
                     f"{r.get('from')} -> {r.get('to')}")
    return "\n".join(lines)


def send_telegram(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat):
        print("[i] Chưa đặt TELEGRAM_BOT_TOKEN/CHAT_ID — bỏ qua gửi Telegram.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=10) as r:
            return r.status == 200
    except Exception as e:
        print(f"[!] Gửi Telegram lỗi: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff", default="inventory/diff.json")
    ap.add_argument("--out", default="inventory/last_alert.txt")
    args = ap.parse_args()

    with open(args.diff, encoding="utf-8") as f:
        d = json.load(f)

    if not d.get("has_change"):
        print("[i] Không có thay đổi — không cảnh báo.")
        return

    msg = build_message(d)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)
    send_telegram(msg)


if __name__ == "__main__":
    main()
