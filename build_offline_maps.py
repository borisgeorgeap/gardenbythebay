#!/usr/bin/env python3
"""
Downloads and stitches high-resolution Google Maps imagery for Gardens by the Bay (Bay South),
and generates offline static Google Map views for each location.
"""
import sys
sys.path.append("/Users/boris/Library/Python/3.9/lib/python/site-packages")
from PIL import Image, ImageDraw
import urllib.request
import math
import os
import io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

OUT_DIR = Path(__file__).resolve().parent / "images" / "maps"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Bounding box covering Bay South (Gardens by the Bay):
# North: 1.2890, South: 1.2765
# West: 103.8575, East: 103.8725
ZOOM = 18

def lat_lng_to_tile_xy(lat_deg, lng_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lng_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return (xtile, ytile)

def tile_xy_to_lat_lng(x, y, zoom):
    n = 2.0 ** zoom
    lng_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lng_deg)

x1, y1 = lat_lng_to_tile_xy(1.2890, 103.8575, ZOOM)
x2, y2 = lat_lng_to_tile_xy(1.2765, 103.8725, ZOOM)

x_min = int(min(x1, x2))
x_max = int(max(x1, x2))
y_min = int(min(y1, y2))
y_max = int(max(y1, y2))

cols = x_max - x_min + 1
rows = y_max - y_min + 1
width = cols * 256
height = rows * 256

print(f"Zoom {ZOOM}: cols={cols}, rows={rows}, resolution={width}x{height}, total tiles={cols*rows}")

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

def fetch_tile(args):
    lyrs, x, y = args
    url = f"https://mt1.google.com/vt/lyrs={lyrs}&x={x}&y={y}&z={ZOOM}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return (x, y, resp.read())
    except Exception as e:
        print(f"Error tile {x},{y}: {e}")
        return (x, y, None)

def stitch_layer(lyrs, out_filename):
    print(f"Fetching {cols*rows} tiles for {out_filename}...")
    tasks = [(lyrs, x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1)]
    img = Image.new("RGB", (width, height))
    with ThreadPoolExecutor(max_workers=8) as executor:
        for x, y, data in executor.map(fetch_tile, tasks):
            if data:
                tile = Image.open(io.BytesIO(data)).convert("RGB")
                px = (x - x_min) * 256
                py = (y - y_min) * 256
                img.paste(tile, (px, py))
    img.save(out_filename, quality=90)
    print(f"Saved {out_filename} ({width}x{height})")
    return img

if __name__ == "__main__":
    hybrid_img = stitch_layer("y", "google-hybrid-map.jpg")
    roadmap_img = stitch_layer("m", "google-roadmap.jpg")
    print("Done building master Google maps.")
