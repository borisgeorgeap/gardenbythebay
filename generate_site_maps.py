#!/usr/bin/env python3
"""
Generate offline Google Map snapshot images for every location from the stitched Google roadmap.
Outputs images/maps/<loc-id>.jpg (600x400 with styled Google marker).
"""
import sys
sys.path.append("/Users/boris/Library/Python/3.9/lib/python/site-packages")
from PIL import Image, ImageDraw
import math
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "images" / "maps"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ZOOM = 18

def lat_lng_to_tile_xy(lat_deg, lng_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lng_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return (xtile, ytile)

# Exact bounding box used in build_offline_maps.py:
x1, y1 = lat_lng_to_tile_xy(1.2890, 103.8575, ZOOM)
x2, y2 = lat_lng_to_tile_xy(1.2765, 103.8725, ZOOM)
x_min = int(min(x1, x2))
y_min = int(min(y1, y2))

# Coordinates for all locations, derived from positions located on google-roadmap.jpg's
# own place labels (see GOOGLE_DATA in index.html).
COORDS = {
    "golden-garden": (1.28248, 103.86577, "#e5007d"),
    "the-canopy": (1.28363, 103.86549, "#e5007d"),
    "flower-dome": (1.28464, 103.86469, "#e5007d"),
    "cloud-forest": (1.2839, 103.86606, "#e5007d"),
    "floral-clock": (1.28348, 103.86498, "#e5007d"),
    "supertree-grove": (1.28201, 103.8639, "#e5007d"),
    "ocbc-skyway": (1.28247, 103.86416, "#e5007d"),
    "supertree-observatory": (1.28213, 103.86376, "#e5007d"),
    "discovery": (1.28023, 103.86325, "#e5007d"),
    "web-of-life": (1.28041, 103.86375, "#e5007d"),
    "fruits-and-flowers": (1.28056, 103.8643, "#e5007d"),
    "understorey": (1.28159, 103.86494, "#e5007d"),
    "world-of-palms": (1.28181, 103.86496, "#e5007d"),
    "secret-life-of-trees": (1.28263, 103.86489, "#e5007d"),
    "indian-garden": (1.28325, 103.86439, "#e5007d"),
    "chinese-garden": (1.28308, 103.86352, "#e5007d"),
    "malay-garden": (1.28253, 103.86294, "#e5007d"),
    "colonial-garden": (1.28136, 103.86286, "#e5007d"),
    "planet": (1.28092, 103.86224, "#e5007d"),
    "the-meadow": (1.27951, 103.86225, "#e5007d"),
    "serene-garden": (1.27851, 103.86086, "#e5007d"),
    "sun-pavilion": (1.28306, 103.86662, "#e5007d"),
    "childrens-garden": (1.28339, 103.86697, "#e5007d"),
    "the-canyon": (1.28375, 103.86658, "#e5007d"),
    "silver-garden": (1.28439, 103.8635, "#e5007d"),
    "floral-fantasy": (1.28182, 103.86118, "#e5007d"),
    "active-garden": (1.28563, 103.86216, "#e5007d"),
    "kingfisher-wetlands": (1.28208, 103.86773, "#e5007d"),
    "starbucks-plaza": (1.28273, 103.8653, "#f6c400"),
    "mcdonalds": (1.28287, 103.86541, "#f6c400"),
    "conservatory-cafe": (1.28373, 103.86543, "#f6c400"),
    "tunglok-douraku": (1.28445, 103.86536, "#f6c400"),
    "marguerite-hortus": (1.28491, 103.86418, "#f6c400"),
    "finnwood": (1.28363, 103.86703, "#f6c400"),
    "satay-by-the-bay": (1.28239, 103.8686, "#f6c400"),
    "starbucks-waterfront": (1.28578, 103.86207, "#f6c400"),
    "janice-wong": (1.28225, 103.86365, "#f6c400"),
    "shake-shack": (1.28375, 103.86529, "#f6c400"),
    "hopscotch": (1.28145, 103.8615, "#f6c400"),
    "jurassic-nest": (1.28113, 103.8643, "#f6c400"),
    "calabash-room": (1.28159, 103.86442, "#f39200"),
    "cannonball-room": (1.28157, 103.86431, "#f39200"),
    "colonnade": (1.28249, 103.86451, "#f39200"),
    "friends-centre": (1.28341, 103.86553, "#f39200"),
    "bayfront-pavilion": (1.2811, 103.86111, "#f39200"),
    "ficus-room": (1.28547, 103.86229, "#f39200"),
    "west-lawn": (1.28401, 103.86212, "#f39200"),
    "garden-pod": (1.27833, 103.86147, "#f39200"),
    "imba-theatre": (1.28322, 103.86186, "#f39200"),
    "visitor-services": (1.28373, 103.86552, "#2e2346"),
    "bayfront-plaza": (1.28083, 103.86083, "#2e2346"),
    "drop-off": (1.28198, 103.86595, "#2e2346"),
    "main-entrance": (1.28062, 103.86606, "#2e2346"),
    "bayfront-mrt": (1.28188, 103.85892, "#2e2346"),
    "gbtb-mrt": (1.27974, 103.86798, "#2e2346"),
    "parking-main": (1.28164, 103.86628, "#2e2346"),
    "parking-bayfront": (1.27974, 103.86063, "#2e2346"),
    "parking-satay": (1.28178, 103.86845, "#2e2346"),
    "toilets-grove": (1.28275, 103.86333, "#2e2346"),
    "toilets-meadow": (1.27849, 103.86176, "#2e2346"),
    "toilets-active": (1.28521, 103.86245, "#2e2346"),
    "shuttle-bayfront": (1.28138, 103.86128, "#2e2346"),
}

def draw_pin(draw, cx, cy, color):
    # Draw drop shadow
    draw.ellipse([cx - 8, cy - 2, cx + 8, cy + 5], fill=(0, 0, 0, 70))
    # Pin shape: circle at top, triangle pointing down to (cx, cy)
    r = 16
    top_cy = cy - 26
    # Pin head
    draw.ellipse([cx - r, top_cy - r, cx + r, top_cy + r], fill=color, outline="#ffffff", width=2)
    # Inner dot
    ir = 6
    draw.ellipse([cx - ir, top_cy - ir, cx + ir, top_cy + ir], fill="#ffffff")
    # Pin point triangle
    draw.polygon([(cx - 9, top_cy + 10), (cx + 9, top_cy + 10), (cx, cy)], fill=color)

def main():
    roadmap = Image.open("google-roadmap.jpg").convert("RGB")
    W, H = roadmap.size
    crop_w, crop_h = 600, 380

    for loc_id, (lat, lng, color) in COORDS.items():
        xtile, ytile = lat_lng_to_tile_xy(lat, lng, ZOOM)
        px = int((xtile - x_min) * 256)
        py = int((ytile - y_min) * 256)

        # Center crop on (px, py)
        x_start = max(0, min(W - crop_w, px - crop_w // 2))
        y_start = max(0, min(H - crop_h, py - crop_h // 2))

        crop = roadmap.crop((x_start, y_start, x_start + crop_w, y_start + crop_h)).copy()
        draw = ImageDraw.Draw(crop, "RGBA")

        # Pin position relative to crop
        pin_cx = px - x_start
        pin_cy = py - y_start
        draw_pin(draw, pin_cx, pin_cy, color)

        # Subtle Google watermark/branding in bottom-right corner
        draw.rectangle([crop_w - 75, crop_h - 22, crop_w - 6, crop_h - 6], fill=(255, 255, 255, 210))
        draw.text((crop_w - 70, crop_h - 20), "Google", fill="#5f6368")

        dest = OUT_DIR / f"{loc_id}.jpg"
        crop.save(dest, quality=88)

    print(f"Generated {len(COORDS)} offline site map images in {OUT_DIR}")

if __name__ == "__main__":
    main()
