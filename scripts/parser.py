#!/usr/bin/env python3
"""ĐT-02 · parser.py — chuyển kết quả quét Nmap (XML) thành danh mục tài sản.

Đọc một hoặc nhiều file XML (-oX của Nmap), trích host/cổng/dịch vụ/phiên bản và
kết quả NSE, gán chủ sở hữu từ owners.csv, giữ first_seen/last_seen nếu có
inventory cũ, rồi ghi ra JSON và CSV.

Ví dụ:
  python3 parser.py -x scans/20261103-2010/*.xml \
      --owners inventory/owners.csv \
      --prev inventory/assets.json \
      --out-json inventory/assets.json --out-csv inventory/assets.csv
"""
import argparse, csv, glob, json, os, sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FIELDS = ["host", "ip", "mac", "os", "port", "proto", "service",
          "version", "owner", "risk", "first_seen", "last_seen"]


def now_iso():
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M")


def load_owners(path):
    owners = {}
    if path and os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ip = (row.get("ip") or "").strip()
                if ip:
                    owners[ip] = (row.get("owner") or "").strip()
    return owners


def parse_xml(path):
    """Trả về list bản ghi (dict) từ một file XML Nmap."""
    recs = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f"[!] Bỏ qua {path}: XML lỗi ({e})", file=sys.stderr)
        return recs

    for host in root.findall("host"):
        if (host.find("status") is not None
                and host.find("status").get("state") != "up"):
            continue
        ip = mac = ""
        for addr in host.findall("address"):
            kind = addr.get("addrtype")
            if kind == "ipv4":
                ip = addr.get("addr", "")
            elif kind == "mac":
                mac = addr.get("addr", "")
        if not ip:
            continue

        os_name = ""
        osmatch = host.find("./os/osmatch")
        if osmatch is not None:
            os_name = osmatch.get("name", "")

        # script chạy ở cấp host (vd smb-protocols)
        host_scripts = {s.get("id"): (s.get("output") or "").strip()
                        for s in host.findall("./hostscript/script")}

        ports_el = host.find("ports")
        if ports_el is None:
            continue
        for port in ports_el.findall("port"):
            state = port.find("state")
            if state is None or state.get("state") != "open":
                continue
            svc = port.find("service")
            service = version = ""
            if svc is not None:
                service = svc.get("name", "")
                version = " ".join(filter(None, [
                    svc.get("product", ""), svc.get("version", ""),
                    svc.get("extrainfo", "")])).strip()
            scripts = dict(host_scripts)
            for s in port.findall("script"):
                scripts[s.get("id")] = (s.get("output") or "").strip()

            recs.append({
                "host": "", "ip": ip, "mac": mac, "os": os_name,
                "port": int(port.get("portid")),
                "proto": port.get("protocol", ""),
                "service": service, "version": version,
                "owner": "", "risk": "", "scripts": scripts,
            })
    return recs


def key(r):
    return (r["ip"], r["port"], r["proto"])


def main():
    ap = argparse.ArgumentParser(description="Nmap XML -> inventory")
    ap.add_argument("-x", "--xml", nargs="+", required=True,
                    help="file XML hoặc glob, ví dụ scans/*/*.xml")
    ap.add_argument("--owners", help="owners.csv (ip,owner,host)")
    ap.add_argument("--prev", help="inventory JSON cũ để giữ first_seen")
    ap.add_argument("--out-json", default="inventory/assets.json")
    ap.add_argument("--out-csv", default="inventory/assets.csv")
    args = ap.parse_args()

    files = []
    for pat in args.xml:
        files.extend(sorted(glob.glob(pat)))
    if not files:
        sys.exit("[!] Không tìm thấy file XML nào.")

    owners = load_owners(args.owners)
    host_by_ip = {}
    if args.owners and os.path.exists(args.owners):
        with open(args.owners, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("ip"):
                    host_by_ip[row["ip"].strip()] = (row.get("host") or "").strip()

    prev = {}
    if args.prev and os.path.exists(args.prev):
        with open(args.prev, encoding="utf-8") as f:
            for r in json.load(f):
                prev[(r["ip"], r["port"], r["proto"])] = r

    ts = now_iso()
    merged = {}
    for path in files:
        for r in parse_xml(path):
            k = key(r)
            r["owner"] = owners.get(r["ip"], "")
            r["host"] = host_by_ip.get(r["ip"], "")
            r["first_seen"] = prev.get(k, {}).get("first_seen", ts)
            r["last_seen"] = ts
            merged[k] = r  # bản ghi mới nhất thắng

    records = sorted(merged.values(), key=lambda r: (r["ip"], r["port"]))

    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow(r)

    print(f"[+] {len(records)} dịch vụ từ {len(files)} file XML "
          f"-> {args.out_json}, {args.out_csv}")


if __name__ == "__main__":
    main()
