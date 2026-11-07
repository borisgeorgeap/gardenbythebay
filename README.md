# Gardens by the Bay (Bay South) Explorer

An interactive, offline-ready web application for exploring **Gardens by the Bay (Bay South)** in Singapore. Includes attraction guides, dining spots, visitor amenities, offline Google maps, site photos, and QR codes for walking directions.

---

## Features

- **Multi-Layer Map Viewer**:
  - **Park Map**: Official illustrated park map (`bay-south-map.jpg`) with numbered attraction markers and icons.
  - **Google Satellite**: High-resolution stitched satellite & hybrid imagery (`google-hybrid-map.jpg`, Zoom 18, 3072×2560).
  - **Google Roads**: Clean street and walking path roadmap (`google-roadmap.jpg`, Zoom 18, 3072×2560).
  - Pins smoothly transition between illustrated and real-world geographic coordinates.
  - Smooth pan and zoom support (pinch, scroll, or on-screen buttons) powered by Panzoom.
- **Offline Google Maps for 53 Locations**:
  - Every attraction, dining spot, and amenity features a static Google map snapshot with a pinpoint marker and GPS coordinates (`images/maps/<id>.jpg`).
  - Seamlessly viewable 100% offline.
  - Includes a one-click toggle to open the live interactive Google Map embed when an internet connection is available.
- **Site Photos & Credits**:
  - High-resolution photos bundled offline (`images/<id>.jpg`).
  - Includes Google Maps community photos and freely licensed Wikimedia Commons photos.
  - Clear attribution and licensing metadata tracked in `images/credits.js`.
  - Direct "Google Photos" action button to open user reviews and galleries on Google Maps.
- **QR Code Navigation**:
  - Generates instant QR codes for walking directions on mobile devices.
  - Works with any phone camera without needing an app installed.
- **Fast Search & Filter**:
  - Real-time instant search across names, categories, and descriptions.
  - Category chips: Attractions, Dining, and Amenities.

---

## Quick Start

Open `index.html` in any modern web browser:

```bash
# Using Python's built-in HTTP server:
python3 -m http.server 8000
```

Then visit [http://localhost:8000](http://localhost:8000) in your browser.

---

## Maintenance Scripts

All scripts use Python 3 and standard libraries (with Pillow for map stitching):

### 1. Build Offline Google Master Maps
Downloads Google Maps tiles at Zoom 18 and stitches `google-hybrid-map.jpg` and `google-roadmap.jpg`:

```bash
python3 build_offline_maps.py
```

### 2. Generate Offline Site Maps
Crops 600×380 static maps with styled pinpoint markers for all 53 locations into `images/maps/`:

```bash
python3 generate_site_maps.py
```

### 3. Fetch / Update Location Photos
Downloads verified Google Maps photos and Wikimedia Commons landmark photos into `images/` and updates `images/credits.js`:

```bash
python3 fetch_photos.py          # fetch missing photos
python3 fetch_photos.py --force  # re-fetch all photos
```

---

## File Structure

```
├── index.html               # Main interactive web application
├── bay-south-map.jpg        # Illustrated park map (2599×1772)
├── google-hybrid-map.jpg    # Google Satellite & Hybrid master map (3072×2560)
├── google-roadmap.jpg       # Google Roadmap master map (3072×2560)
├── build_offline_maps.py    # Master map tile fetcher and stitcher
├── generate_site_maps.py    # 53 offline site map generator
├── fetch_photos.py          # Photo fetcher and attribution generator
└── images/
    ├── credits.js           # Photo attribution metadata
    ├── *.jpg                # High-resolution site photos
    └── maps/                # 53 offline Google map site snapshots
        └── *.jpg
```

---

## License & Attribution

- Illustrated map © Gardens by the Bay.
- Map imagery © Google Maps.
- Location photos attributed individually in `images/credits.js` under their respective licenses (Google Maps community contributions / Creative Commons / Public Domain).
