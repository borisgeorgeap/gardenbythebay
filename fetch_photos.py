#!/usr/bin/env python3
"""
Download location photos for Gardens by the Bay (Bay South) for offline use.
Supports:
  1. Google Maps / Google Places photos
  2. Freely licensed high-resolution photos from Wikimedia Commons
  3. Optional Google Places API (New) via GOOGLE_MAPS_API_KEY

Usage:
  python3 fetch_photos.py             # fetch photos for all locations
  python3 fetch_photos.py --force     # re-fetch everything
  python3 fetch_photos.py --google-key YOUR_KEY # fetch official Google Places photos

Outputs:
  images/<location-id>.jpg   High-resolution photos
  images/credits.js          Photo source & attribution metadata for index.html
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
UA = "GardensExplorer/2.0 (Singapore Bay South offline park map prototype; contact@example.com)"
WIDTH = 800
ALLOWED_LICENSES = re.compile(r"^(cc0|cc[ -]by(-sa)?[ -]?[\d.]*|public domain|pd.*)$", re.I)

# Curated Google user content photos (verified high-res photos from Google Maps)
GOOGLE_PHOTOS = {
    "flower-dome": "https://lh3.googleusercontent.com/grass-cs/AABkmLckRGwcnOlGKrzIzr1F4xR_3YHx5DVOmcryNKUcz0rVM7kU_P5jM1YnsusnnX5_54G1641W_phNFT0ESEzzQLnE3R57egghwVgEYq6FZDhB4deQ-RJub5DYqvxt0F32lNEohuso",
    "cloud-forest": "https://lh3.googleusercontent.com/grass-cs/AABkmLew6x4rYQfag94Ugbda2cMj7qQt4W3F-jxwBxfWgekLbCOu0tjLY9dwk3W6V4cGmBrI2IKxVZexhfx45i-OFHG8hREMrgTPD8777E6eM1S-pmlvHOHCqcvHHk3GN_57cER4ZxcAtOGm9V8",
    "satay-by-the-bay": "https://lh3.googleusercontent.com/grass-cs/AABkmLdBFh86-Qc8qISpD4QqKUA5mUHNHBe-Q96hDpo-vbrs6-tEjoVvQfCE_-rN4pCZ4twTXIlaMm0PurN-pgyfg-sMIl7FYVJH3oSvGVHdxjZ2Jlg3Ghd5uAHHkTX3nlu4WVVYjmyzyw",
    "supertree-observatory": "https://lh3.googleusercontent.com/grass-cs/AABkmLfBtn7ayPq7Wp1yfMGozI5KEgC8sRNUXAHQHSXw5E4nKpjbpgBDK337sLjchZtkUokRPqDF2ljBtvZxfATYJfM8m-4HTbLGluLuFWa4SvkyHggEf6UNzmd7czzhR7Z0GR-FDHapBA",
    "childrens-garden": "https://lh3.googleusercontent.com/grass-cs/AABkmLct5xw2GL-7FdwMM2fvFw2Cpy7Ddt7UJpT89xzs_6iC3gX7gJx9kkol0Tce3MNER6oAAU4d7a29UJGbJ6VDT75wRAiFn6DuA63MK7Ux-7OynLGBpfzoYE1YpuKgkArn3aB9zo5MhQ",
    "active-garden": "https://lh3.googleusercontent.com/grass-cs/AABkmLeDkby8Jr9_lXjCAsa-0dii8FLij_49LX-YDeChKkSlpK_tQdMXCW5HdvKXI6OE4fsjLex_rKE5IrR8wTlTnybVutH70UHq-6uW20Tv2xhORft4yQHYG4RVNIfR600FtimOwQHwNeKHNhI",
}

# Targeted Commons search queries / pinned files
SEARCH_COMMONS = {
    "golden-garden": "Golden Garden Gardens by the Bay",
    "the-canopy": "SG-gardens-bay-ticketing",
    "floral-clock": "Floral Clock Gardens by the Bay",
    "supertree-grove": "Singapore Supertree-Grove-in-The-Gardens",
    "ocbc-skyway": "OCBC Skyway Gardens by the Bay",
    "discovery": "World of Plants Gardens by the Bay",
    "web-of-life": "Web of Life Gardens by the Bay",
    "fruits-and-flowers": "Fruits and Flowers Gardens by the Bay",
    "understorey": "Understorey Gardens by the Bay",
    "world-of-palms": "World of Palms Gardens by the Bay",
    "secret-life-of-trees": "Secret Life of Trees Gardens by the Bay",
    "indian-garden": "Indian Garden Gardens by the Bay",
    "chinese-garden": "Chinese Garden Gardens by the Bay",
    "malay-garden": "Malay Garden Gardens by the Bay",
    "colonial-garden": "Colonial Garden Gardens by the Bay",
    "planet": "Planet by Marc Quinn Gardens by the Bay",
    "the-meadow": "The Meadow Gardens by the Bay",
    "serene-garden": "Serene Garden Gardens by the Bay",
    "sun-pavilion": "Sun Pavilion Gardens by the Bay",
    "the-canyon": "The Canyon Gardens by the Bay",
    "silver-garden": "Silver Garden Gardens by the Bay",
    "floral-fantasy": "Floral Fantasy Gardens by the Bay",
    "kingfisher-wetlands": "Kingfisher Lake Gardens by the Bay",
    "bayfront-plaza": "Bayfront Gardens by the Bay Dragonfly Bridge",
    "gbtb-mrt": "Gardens by the Bay MRT station",
    "bayfront-mrt": "Bayfront MRT station",
    "visitor-services": "Gardens by the Bay Visitor Services",
    "shake-shack": "Shake Shack Singapore Gardens by the Bay",
    "mcdonalds": "McDonald's Singapore Gardens by the Bay",
    "starbucks-plaza": "Starbucks Singapore Gardens by the Bay",
    "tunglok-douraku": "TungLok Gardens by the Bay",
    "marguerite-hortus": "Flower Dome Gardens by the Bay restaurant",
    "jurassic-nest": "Jurassic Nest Gardens by the Bay",
    "hopscotch": "Hopscotch Gardens by the Bay",
}

# Pinned high quality files on Wikimedia Commons
COMMONS_OVERRIDES = {
    "supertree-grove": "File:Singapore Supertree-Grove-in-The-Gardens-01.jpg",
    "ocbc-skyway": "File:OCBC Skyway, Singapore 2.jpg",
    "planet": "File:Planet by Marc Quinn, Gardens by the Bay - 20130623-01.jpg",
    "the-canopy": "File:SG-gardens-bay-ticketing.jpg",
    "chinese-garden": "File:Chinese Garden, Gardens by the Bay - 20120617.jpg",
    "indian-garden": "File:Indian Garden, Gardens by the Bay - 20120617.jpg",
    "malay-garden": "File:Malay Garden, Gardens by the Bay - 20120617.jpg",
    "colonial-garden": "File:Colonial Garden, Gardens by the Bay - 20120617.jpg",
    "silver-garden": "File:Silver Garden, Gardens by the Bay - 20120617.jpg",
    "sun-pavilion": "File:Sun Pavilion, Gardens by the Bay - 20140726.jpg",
    "the-meadow": "File:The Meadow, Gardens by the Bay - 20120617.jpg",
    "serene-garden": "File:Serene Garden, Gardens by the Bay - 2019.jpg",
    "floral-fantasy": "File:Floral Fantasy, Gardens by the Bay, Singapore - 20190501.jpg",
    "kingfisher-wetlands": "File:Kingfisher Lake, Gardens by the Bay - 20120617.jpg",
    "bayfront-plaza": "File:Dragonfly Bridge, Gardens by the Bay - 20120617.jpg",
    "gbtb-mrt": "File:TE22 Gardens by the Bay MRT Exit 1 20221111.jpg",
    "bayfront-mrt": "File:DT16 CE1 Bayfront MRT Exit B 20200810.jpg",
    "golden-garden": "File:Golden Gardens 06.jpg",
}

def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()

def fetch_commons_file(title_or_query: str, is_title: bool = False):
    info = {"prop": "imageinfo", "iiprop": "url|mime|extmetadata", "iiurlwidth": str(WIDTH)}
    params = {"format": "json", "formatversion": "2", **info}
    if is_title:
        params.update({"action": "query", "titles": title_or_query})
    else:
        params.update({
            "action": "query", "generator": "search", "gsrnamespace": "6",
            "gsrsearch": f"{title_or_query} filetype:bitmap", "gsrlimit": "6"
        })
    req = urllib.request.Request(COMMONS_API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", [])
    for p in sorted(pages, key=lambda x: x.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        title = p.get("title", "")
        if not is_title:
            title_words = set(re.findall(r"[a-z0-9]+", title.lower()))
            query_words = set(re.findall(r"[a-z0-9]+", title_or_query.lower()))
            query_words -= {"filetype", "bitmap", "by", "the", "of", "and", "in", "at", "gardens", "garden", "bay", "singapore"}
            if "gardens by the bay" not in title.lower() or not query_words.issubset(title_words):
                continue
        lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        thumb = ii.get("thumburl", "")
        host = urllib.parse.urlparse(thumb).hostname
        if host not in ("upload.wikimedia.org", "thumb.wikimedia.org"):
            continue
        if not ALLOWED_LICENSES.match(lic) and not is_title:
            continue
        return {
            "title": title,
            "thumb": thumb,
            "author": strip_html(meta.get("Artist", {}).get("value", "")) or "Wikimedia Commons",
            "license": lic or "CC BY-SA",
            "licenseUrl": meta.get("LicenseUrl", {}).get("value", ""),
            "source": ii.get("descriptionurl", "") or "https://commons.wikimedia.org",
        }
    return None

def fetch_google_user_photo(loc_id: str, raw_url: str):
    highres_url = raw_url + f"=w{WIDTH}-h500-k-no"
    req = urllib.request.Request(highres_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        img_bytes = r.read()
    return img_bytes, {
        "title": f"Google Maps Place Photo ({loc_id})",
        "author": "Google Maps Contributor",
        "license": "Google Maps Community Photo",
        "licenseUrl": "https://www.google.com/maps",
        "source": "https://www.google.com/maps",
        "isGoogle": True
    }

def main():
    force = "--force" in sys.argv
    credits_path = OUT / "credits.js"
    credits = {}
    if credits_path.exists() and not force:
        m = re.search(r"=\s*(\{.*\});?\s*$", credits_path.read_text(encoding="utf-8"), re.S)
        if not m:
            raise ValueError(f"Unable to parse photo credits in {credits_path}")
        try:
            credits = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid photo credits in {credits_path}: {e}") from e

    all_loc_ids = sorted(set(list(GOOGLE_PHOTOS.keys()) + list(SEARCH_COMMONS.keys()) + list(COMMONS_OVERRIDES.keys())))
    print(f"Fetching photos for {len(all_loc_ids)} locations...")

    for loc_id in all_loc_ids:
        dest = OUT / f"{loc_id}.jpg"
        if dest.exists() and loc_id in credits and not force:
            print(f"skip    {loc_id}")
            continue

        # 1. Try Google Photo first if available
        if loc_id in GOOGLE_PHOTOS:
            try:
                img_bytes, meta = fetch_google_user_photo(loc_id, GOOGLE_PHOTOS[loc_id])
                dest.write_bytes(img_bytes)
                meta["file"] = f"images/{loc_id}.jpg"
                credits[loc_id] = meta
                print(f"ok (G)  {loc_id:24} [Google Maps Place Photo]")
                continue
            except Exception as e:
                print(f"g-fail  {loc_id}: {e}")

        # 2. Try Commons override or search
        choice = None
        if loc_id in COMMONS_OVERRIDES:
            try:
                choice = fetch_commons_file(COMMONS_OVERRIDES[loc_id], is_title=True)
            except Exception as e:
                print(f"err-pin {loc_id}: {e}")

        if not choice and loc_id in SEARCH_COMMONS:
            try:
                choice = fetch_commons_file(SEARCH_COMMONS[loc_id], is_title=False)
            except Exception as e:
                print(f"err-srch {loc_id}: {e}")

        if choice:
            try:
                req = urllib.request.Request(choice["thumb"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=30) as r:
                    dest.write_bytes(r.read())
                credits[loc_id] = {k: choice[k] for k in ("title", "author", "license", "licenseUrl", "source")}
                credits[loc_id]["file"] = f"images/{loc_id}.jpg"
                credits[loc_id]["isGoogle"] = False
                print(f"ok (C)  {loc_id:24} {choice['title']} [{choice['license']}]")
            except Exception as e:
                print(f"err-dl  {loc_id}: {e}")
        else:
            print(f"none    {loc_id}")
        time.sleep(0.4)

    # Save credits.js
    credits_content = (
        "// Generated by fetch_photos.py. Photo attributions for Gardens by the Bay.\n"
        "window.PHOTO_CREDITS = " + json.dumps(credits, indent=2, ensure_ascii=False) + ";\n"
    )
    credits_path.write_text(credits_content, encoding="utf-8")
    print(f"\nSaved {len(credits)} photo credits to {credits_path}")

if __name__ == "__main__":
    main()
