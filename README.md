# Google Maps Business Scraper

A modern desktop application for extracting business data from Google Maps with a beautiful UI.

## Features

- 🔍 Search businesses by tag, region, and city
- 📞 Extract name, phone number, and location
- 🚫 Automatic deduplication
- 💾 Export to Excel/CSV
- 🎨 Modern Material Design UI

## Installation

1. Install Python 3.9+
2. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Run the application:
```bash
python main.py
```

## Usage

1. Enter business tag (e.g., "Real Estate Office", "Law Firm")
2. Select region (e.g., "Makkah")
3. Select city (e.g., "Jeddah")
4. Click "Start Search"
5. Export results when complete

## Notes

- The browser will open visibly during scraping
- Random delays are used to avoid bot detection
- Duplicate entries are automatically filtered
