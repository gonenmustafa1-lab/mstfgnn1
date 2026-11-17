#!/usr/bin/env python3
"""Refresh TV1's free, official-tier Turkish and sports M3U sub-playlists."""
from pathlib import Path
from urllib.request import Request, urlopen
import re
import unicodedata
import os

BASE = "https://raw.githubusercontent.com/Shahrukhalid/nexonic-iptv/main/playlists/"
ROOT = Path(__file__).resolve().parents[1]

def fetch(path):
    req = Request(BASE + path, headers={"User-Agent": "MustafaTV1-Playlist-Sync/1.0"})
    with urlopen(req, timeout=45) as response:
        data = response.read().decode("utf-8-sig")
    if not data.lstrip().startswith("#EXTM3U"):
        raise RuntimeError(f"Invalid M3U from {path}")
    return data

def entries(text):
    lines = text.replace("\r", "").splitlines()
    result = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("#EXTINF:"):
            i += 1
            continue
        info = lines[i]
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].startswith("#")):
            j += 1
        if j < len(lines) and lines[j].strip().startswith(("http://", "https://")):
            result.append((info, lines[j].strip()))
        i = j + 1
    return result

def label(info):
    return info.split(",", 1)[1].strip() if "," in info else ""

def normal(value):
    value = unicodedata.normalize("NFD", value.lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]", "", value)

def set_group(info, prefix):
    match = re.search(r'group-title="([^"]*)"', info)
    group = match.group(1) if match else "GENEL"
    replacement = f'group-title="{prefix} / {group}"'
    if match:
        return info[:match.start()] + replacement + info[match.end():]
    return info.replace(",", f' {replacement},', 1)

def write_m3u(path, title, items):
    if not items:
        raise RuntimeError(f"Refusing to replace {path} with an empty playlist")
    body = "#EXTM3U\n# " + title + "\n"
    body += "\n".join(info + "\n" + url for info, url in items) + "\n"
    target = ROOT / path
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    os.replace(tmp, target)

def main():
    base_sports = entries((ROOT / "spor-base.m3u").read_text(encoding="utf-8"))
    official_sports = [
        (set_group(info, "SPOR"), url)
        for info, url in entries(fetch("categories/sports.m3u"))
        if 'x-tier="community"' not in info
    ]
    sports = []
    seen_urls, seen_names = set(), set()
    for info, url in base_sports + official_sports:
        key = normal(label(info))
        if url in seen_urls or (key and key in seen_names):
            continue
        sports.append((info, url))
        seen_urls.add(url)
        if key:
            seen_names.add(key)
    if len(sports) < 10:
        raise RuntimeError(f"Only {len(sports)} official/free sports feeds; keeping old file")

    known = entries((ROOT / "tv-kanallari.m3u").read_text(encoding="utf-8"))
    known_urls = {url for _, url in known}
    known_names = {normal(label(info)) for info, _ in known}
    extras = []
    for info, url in entries(fetch("countries/tr.m3u")):
        if 'x-tier="community"' in info:
            continue
        if not re.search(r'tvg-language="[^"]*Turkish', info, re.I):
            continue
        key = normal(label(info))
        if url in known_urls or (key and key in known_names):
            continue
        extras.append((set_group(info, "EK TÜRKİYE"), url))
        known_urls.add(url)
        if key:
            known_names.add(key)
    if len(extras) < 5:
        raise RuntimeError(f"Only {len(extras)} official-tier Turkish extras; keeping old file")

    # Only write after both remote sources passed validation.
    write_m3u("spor.m3u", "Nexonic official-tier sports streams + TV1's free Turkish sports sources", sports)
    write_m3u("tv-ekstra.m3u", "Turkish-language entries without the community/unverified-rights tag", extras)
    print(f"Updated sports={len(sports)}, extra_turkish={len(extras)}")

if __name__ == "__main__":
    main()
