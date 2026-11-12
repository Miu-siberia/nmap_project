#!/usr/bin/env python3
"""ĐT-02 · diff.py — so sánh hai inventory JSON, phát hiện thay đổi trái phép.

Liệt kê dịch vụ MỚI (shadow IT / cổng mới mở), dịch vụ MẤT và thay đổi phiên bản.
Trả về mã thoát 1 nếu có thay đổi (để run_audit.sh kích hoạt cảnh báo).

Ví dụ:
  python3 diff.py --old inventory/prev.json --new inventory/assets.json \
      --out inventory/diff.json
"""
import argparse, json, sys


def load(path):
    with open(path, encoding="utf-8") as f:
        return {(r["ip"], r["port"], r["proto"]): r for r in json.load(f)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default="inventory/diff.json")
    args = ap.parse_args()

    old, new = load(args.old), load(args.new)
    added = [new[k] for k in new.keys() - old.keys()]
    removed = [old[k] for k in old.keys() - new.keys()]
    changed = []
    for k in old.keys() & new.keys():
        if old[k].get("version") != new[k].get("version"):
            changed.append({"ip": k[0], "port": k[1], "proto": k[2],
                            "service": new[k].get("service"),
                            "from": old[k].get("version"),
                            "to": new[k].get("version")})

    result = {
        "added": sorted(added, key=lambda r: (r["ip"], r["port"])),
        "removed": sorted(removed, key=lambda r: (r["ip"], r["port"])),
        "changed": changed,
        "has_change": bool(added or removed or changed),
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[+] Diff: +{len(added)} mới, -{len(removed)} mất, ~{len(changed)} đổi phiên bản")
    for r in added:
        print(f"    [MỚI] {r['ip']}:{r['port']} {r.get('service','')} "
              f"(risk={r.get('risk','?')})  <-- kiểm tra shadow IT")
    for r in removed:
        print(f"    [MẤT] {r['ip']}:{r['port']} {r.get('service','')}")

    sys.exit(1 if result["has_change"] else 0)


if __name__ == "__main__":
    main()
