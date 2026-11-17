#!/usr/bin/env python3
"""Build a compact Turkish SS IPTV playlist from iptv-org's maintained public stream index.

The upstream project curates and monitors public stream links. This script only selects
a fixed set of Turkish channels and excludes entries explicitly marked geo-blocked or
not 24/7. It cannot guarantee playback on every TV/network.
"""
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
OUTPUT = Path("tv1.m3u")

# tvg-id (without the country suffix) -> (display name, SS IPTV category)
CHANNELS = {
    "TRT1": ("TRT 1", "01 - Ulusal"),
    "ATV": ("ATV", "01 - Ulusal"),
    "KanalD": ("Kanal D", "01 - Ulusal"),
    "StarTV": ("Star TV", "01 - Ulusal"),
    "NOW": ("NOW", "01 - Ulusal"),
    "TV8": ("TV8", "01 - Ulusal"),
    "Kanal7": ("Kanal 7", "01 - Ulusal"),
    "BeyazTV": ("Beyaz TV", "01 - Ulusal"),
    "360": ("360 TV", "01 - Ulusal"),
    "A2TV": ("A2", "01 - Ulusal"),
    "TRTHaber": ("TRT Haber", "02 - Haber"),
    "AHaber": ("A Haber", "02 - Haber"),
    "CNNTurk": ("CNN Türk", "02 - Haber"),
    "NTV": ("NTV", "02 - Haber"),
    "HaberturkTV": ("Habertürk", "02 - Haber"),
    "HalkTV": ("Halk TV", "02 - Haber"),
    "Tele1": ("TELE1", "02 - Haber"),
    "SozcuTV": ("Sözcü TV", "02 - Haber"),
    "HaberGlobal": ("Haber Global", "02 - Haber"),
    "TGRTHaber": ("TGRT Haber", "02 - Haber"),
    "24TV": ("24 TV", "02 - Haber"),
    "TVNET": ("TVNET", "02 - Haber"),
    "UlkeTV": ("Ülke TV", "02 - Haber"),
    "BloombergHT": ("Bloomberg HT", "02 - Haber"),
    "TBMMTV": ("TBMM TV", "02 - Haber"),
    "TRTSpor": ("TRT Spor", "03 - Spor"),
    "TRTSporYildiz": ("TRT Spor Yıldız", "03 - Spor"),
    "ASpor": ("A Spor", "03 - Spor"),
    "HTSporTV": ("HT Spor", "03 - Spor"),
    "TJKTV": ("TJK TV", "03 - Spor"),
    "FBTV": ("FB TV", "03 - Spor"),
    "TRTBelgesel": ("TRT Belgesel", "04 - Belgesel"),
    "TGRTBelgesel": ("TGRT Belgesel", "04 - Belgesel"),
    "TRTCocuk": ("TRT Çocuk", "05 - Çocuk"),
    "MinikaGo": ("Minika GO", "05 - Çocuk"),
    "MinikaCocuk": ("Minika Çocuk", "05 - Çocuk"),
    "CartoonNetwork": ("Cartoon Network", "05 - Çocuk"),
    "TRTMuzik": ("TRT Müzik", "06 - Müzik"),
    "DreamTurk": ("Dream Türk", "06 - Müzik"),
    "PowerTurkTV": ("PowerTürk TV", "06 - Müzik"),
    "Number1TV": ("Number One TV", "06 - Müzik"),
}

def fetch_source():
    req = Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 (compatible; TV1PlaylistUpdater/1.0)"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def parse_entries(text):
    lines = [line.strip() for line in text.splitlines()]
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:"):
            info = line
            url = ""
            j = i + 1
            while j < len(lines):
                candidate = lines[j]
                if candidate and not candidate.startswith("#"):
                    url = candidate
                    break
                j += 1
            if url:
                entries.append((info, url))
            i = j
        i += 1
    return entries

def main():
    source = fetch_source()
    found = {}
    for info, url in parse_entries(source):
        # Entries marked as unavailable for normal continuous viewing are omitted.
        if "[Geo-blocked]" in info or "[Not 24/7]" in info:
            continue
        marker = 'tvg-id="'
        if marker not in info:
            continue
        channel_id = info.split(marker, 1)[1].split('"', 1)[0].split(".", 1)[0]
        if channel_id not in CHANNELS or channel_id in found:
            continue
        found[channel_id] = (info, url)

    output = ["#EXTM3U", "# TV1 - otomatik güncellenen Türkiye kanal listesi",
              "# Kaynak: iptv-org/iptv (topluluk tarafından derlenen herkese açık yayın bağlantıları)",
              "# Yayınların çalışması yayıncı, bölge ve internet sağlayıcısına bağlıdır.", ""]
    count = 0
    for channel_id, (name, group) in CHANNELS.items():
        if channel_id not in found:
            continue
        info, url = found[channel_id]
        # Use stable, short channel names and SS IPTV category names.
        output.append(f'#EXTINF:-1 tvg-id="{channel_id}.tr" tvg-name="{name}" group-title="{group}",{name}')
        output.append(url)
        count += 1

    # Never overwrite a working playlist with an unexpectedly tiny/empty source result.
    if count < 15:
        raise SystemExit(f"Upstream returned only {count} selected channels; keeping existing tv1.m3u unchanged.")
    OUTPUT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT}: {count} channels")

if __name__ == "__main__":
    main()
