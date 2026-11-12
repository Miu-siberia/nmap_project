#!/usr/bin/env python3
"""ĐT-02 · report.py — sinh báo cáo HTML từ inventory và diff.

Ví dụ:
  python3 report.py --inv inventory/assets.json --diff inventory/diff.json \
      --out report.html
"""
import argparse, html, json, os
from collections import Counter
from datetime import datetime

RISK_COLOR = {"cao": "#C0392B", "trung bình": "#D68910", "thấp": "#1E8449"}


def esc(x):
    return html.escape(str(x if x is not None else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inv", default="inventory/assets.json")
    ap.add_argument("--diff", default="inventory/diff.json")
    ap.add_argument("--out", default="report.html")
    args = ap.parse_args()

    with open(args.inv, encoding="utf-8") as f:
        inv = json.load(f)
    diff = {}
    if os.path.exists(args.diff):
        with open(args.diff, encoding="utf-8") as f:
            diff = json.load(f)

    risk = Counter(r.get("risk", "?") for r in inv)
    hosts = sorted({r["ip"] for r in inv})

    rows = ""
    for r in sorted(inv, key=lambda r: (r["ip"], r["port"])):
        c = RISK_COLOR.get(r.get("risk"), "#555")
        rows += (f"<tr><td>{esc(r['ip'])}</td><td>{esc(r.get('host'))}</td>"
                 f"<td>{esc(r['port'])}/{esc(r['proto'])}</td>"
                 f"<td>{esc(r.get('service'))}</td><td>{esc(r.get('version'))}</td>"
                 f"<td>{esc(r.get('owner'))}</td>"
                 f"<td style='color:{c};font-weight:600'>{esc(r.get('risk'))}</td>"
                 f"<td>{esc(r.get('risk_reason'))}</td></tr>")

    diff_html = "<p>Không có dữ liệu diff.</p>"
    if diff:
        def block(title, items, fmt):
            if not items:
                return f"<p><b>{title}:</b> không có.</p>"
            lis = "".join(f"<li>{fmt(x)}</li>" for x in items)
            return f"<p><b>{title}:</b></p><ul>{lis}</ul>"
        diff_html = (
            block("Dịch vụ mới (kiểm tra shadow IT)", diff.get("added", []),
                  lambda r: f"{esc(r['ip'])}:{esc(r['port'])} {esc(r.get('service'))} (risk={esc(r.get('risk'))})")
            + block("Dịch vụ mất", diff.get("removed", []),
                    lambda r: f"{esc(r['ip'])}:{esc(r['port'])} {esc(r.get('service'))}")
            + block("Đổi phiên bản", diff.get("changed", []),
                    lambda r: f"{esc(r['ip'])}:{esc(r['port'])} {esc(r.get('from'))} → {esc(r.get('to'))}"))

    doc = f"""<!DOCTYPE html><html lang="vi"><head><meta charset="utf-8">
<title>ĐT-02 · Báo cáo bề mặt tấn công</title>
<style>
 body{{font-family:Segoe UI,Arial,sans-serif;margin:32px;color:#1a1a1a}}
 h1{{color:#1F3864}} h2{{color:#2E5597;margin-top:28px}}
 table{{border-collapse:collapse;width:100%;font-size:14px}}
 th,td{{border:1px solid #c9d3e0;padding:6px 8px;text-align:left}}
 th{{background:#1F3864;color:#fff}} tr:nth-child(even){{background:#f2f6fa}}
 .cards{{display:flex;gap:16px;margin:16px 0}}
 .card{{flex:1;border:1px solid #c9d3e0;border-radius:10px;padding:16px;text-align:center}}
 .num{{font-size:34px;font-weight:700}}
</style></head><body>
<h1>Báo cáo bề mặt tấn công — ĐT-02</h1>
<p>Sinh ngày {datetime.now():%Y-%m-%d %H:%M} · {len(hosts)} host · {len(inv)} dịch vụ mở</p>
<div class="cards">
 <div class="card"><div class="num" style="color:#C0392B">{risk.get('cao',0)}</div>Rủi ro cao</div>
 <div class="card"><div class="num" style="color:#D68910">{risk.get('trung bình',0)}</div>Trung bình</div>
 <div class="card"><div class="num" style="color:#1E8449">{risk.get('thấp',0)}</div>Thấp</div>
 <div class="card"><div class="num">{len(hosts)}</div>Host</div>
</div>
<h2>Thay đổi so với lần quét trước</h2>
{diff_html}
<h2>Danh mục tài sản</h2>
<table><tr><th>IP</th><th>Host</th><th>Cổng</th><th>Dịch vụ</th><th>Phiên bản</th>
<th>Chủ sở hữu</th><th>Rủi ro</th><th>Lý do</th></tr>
{rows}</table>
</body></html>"""

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"[+] Báo cáo HTML -> {args.out}")


if __name__ == "__main__":
    main()
