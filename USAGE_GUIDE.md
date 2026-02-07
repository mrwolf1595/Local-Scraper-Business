# Installation & Usage Guide

## ✅ Installation Complete!

All dependencies have been installed successfully.

## 🚀 How to Run

### Option 1: Double-click the batch file
```
run_app.bat
```

### Option 2: Run from terminal
```powershell
cd "h:\Local Scraper Business"
.venv\Scripts\python.exe main.py
```

## 📖 How to Use

1. **Launch the Application**: Double-click `run_app.bat`

2. **Enter Search Details**:
   - **Business Tag**: Type of business (e.g., "مكتب عقارات", "Real Estate Office", "مكتب محاماة", "Law Firm")
   - **Region**: The region name (e.g., "مكة", "Makkah")
   - **City**: The city name (e.g., "جدة", "Jeddah")

3. **Start Search**: Click the green "Start Search" button
   - The browser will open automatically
   - Watch the status log for progress
   - Results appear in the table in real-time

4. **Stop Anytime**: Click the red "Stop" button to pause

5. **Export Results**: Click "Export to Excel" button
   - File saved to `exports/` folder
   - Automatic file explorer will open
   - Excel format with all data

## ✨ Features

### ✅ Automatic Deduplication
- Each business has a unique ID from Google Maps
- Duplicate entries are **automatically filtered**
- No manual cleanup needed!

### 📊 Real-Time Updates
- Live data table shows results as they're found
- Status log tracks every step
- See exactly what the scraper is doing

### 🔒 Anti-Bot Protection
- Random delays between actions
- Human-like scrolling behavior
- Browser fingerprint masking
- Passes Google's bot detection

### 🌐 Arabic & English Support
- Supports both Arabic and English search queries
- Proper text encoding in Excel exports
- Mixed language data handled correctly

## 📁 Output Files

Exported files are saved in: `exports/google_maps_export_YYYYMMDD_HHMMSS.xlsx`

Contains:
- Business Name
- Phone Number
- Full Address
- GPS Coordinates (Latitude/Longitude)
- Google Maps URL (clickable link)

## ⚠️ Important Notes

1. **Internet Required**: Active internet connection needed
2. **Browser Opens**: Chrome browser opens automatically (this is normal)
3. **Search Limits**: Google limits results to ~100-120 per search
   - For more results, try narrower searches (specific neighborhoods)
4. **Speed**: Scraping is intentionally slow (2-5 seconds per action) to avoid detection
5. **No Login**: Never sign in to Google - scrapes as guest

## 🔧 Troubleshooting

### Browser doesn't open
```powershell
cd "h:\Local Scraper Business"
.venv\Scripts\playwright.exe install chromium
```

### Missing packages error
```powershell
cd "h:\Local Scraper Business"
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### "No results found"
- Check spelling of business tag, region, city
- Try broader search terms
- Verify internet connection

## 💡 Tips for Best Results

1. **Be Specific**: "مكاتب العقارات في حي النزهة" gets better results than "عقارات"
2. **Use English Location Names**: Google Maps often works better with "Jeddah" vs "جدة"
3. **Small Areas**: Search by neighborhood for complete coverage
4. **Export Often**: Save results after each search session

## 🎯 Example Searches

### Real Estate in Jeddah
- Tag: `مكتب عقارات` or `Real Estate Office`
- Region: `Makkah` or `مكة`
- City: `Jeddah` or `جدة`

### Law Firms in Riyadh
- Tag: `مكتب محاماة` or `Law Firm`
- Region: `Riyadh` or `الرياض`
- City: `Riyadh` or `الرياض`

### Car Dealerships in Dammam
- Tag: `وكالة سيارات` or `Car Dealership`
- Region: `Eastern Province` or `المنطقة الشرقية`
- City: `Dammam` or `الدمام`

## 📞 Support

If you encounter issues:
1. Check the Status Log in the app
2. Verify all input fields are filled
3. Ensure stable internet connection
4. Restart the application

---

**Version**: 1.0  
**Built with**: Python, Flet, Playwright  
**Date**: February 2026
