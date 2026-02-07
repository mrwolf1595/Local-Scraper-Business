# Project Structure

```
Local Scraper Business/
│
├── main.py                 # Main application with Flet UI
├── scraper.py              # Google Maps scraper engine
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run_app.bat            # Windows launcher script
├── README.md              # Project overview
├── USAGE_GUIDE.md         # Detailed usage instructions
├── .gitignore             # Git ignore file
│
├── .venv/                 # Virtual environment (auto-created)
│   └── ...
│
└── exports/               # Output folder (auto-created)
    └── google_maps_export_*.xlsx
```

## File Descriptions

### Core Files

**main.py**
- Flet-based desktop UI
- Input forms, data table, status log
- Export functionality
- Event handling and async integration

**scraper.py**
- Playwright automation engine
- Google Maps navigation and scrolling
- Data extraction (name, phone, address, coordinates)
- Deduplication system using unique place IDs
- Anti-bot detection measures

**config.py**
- Centralized configuration
- Timing delays (random ranges)
- Browser settings
- UI dimensions

### Dependencies

**requirements.txt**
- `flet` - Modern UI framework (Flutter for Python)
- `playwright` - Browser automation
- `pandas` - Data manipulation
- `openpyxl` - Excel export
- `playwright-stealth` - Bot detection bypass

### Scripts

**run_app.bat**
- One-click launcher for Windows
- Automatically activates venv and runs app

## Data Flow

```
User Input (Tag, Region, City)
    ↓
Search Query Built
    ↓
Browser Opens Google Maps
    ↓
Infinite Scroll Loop
    ↓
Extract Place URLs
    ↓
Visit Each Place
    ↓
Extract Details (Name, Phone, Address, GPS)
    ↓
Check Deduplication (Place ID)
    ↓
Add to UI Table (Real-time)
    ↓
Export to Excel
```

## Key Features Implementation

### 🚫 Deduplication
- Extracts unique `Feature ID` or `Data CID` from URLs
- Maintains `seen_ids` set in memory
- Skips duplicates before adding to results

### 🎭 Anti-Bot Measures
- Random delays (2-5 seconds)
- Browser fingerprint masking
- No webdriver detection
- Human-like scrolling

### 🔄 Real-Time UI Updates
- Async event callbacks
- Non-blocking scraper execution
- Live status updates
- Progressive data table population

### 📊 Export System
- Pandas DataFrame conversion
- Excel with proper encoding
- Auto-open file location
- Timestamped filenames
