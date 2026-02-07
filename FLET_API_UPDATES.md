# Flet 0.80+ API Updates

This document outlines the API changes made to support Flet version 0.80+

## Changes Made

### 1. Colors Module
**Old**: `ft.colors.BLUE_700`  
**New**: `from flet import Colors` then `Colors.BLUE_700`

### 2. Icons Module  
**Old**: `ft.icons.SEARCH`  
**New**: `ft.Icons.SEARCH`

### 3. Buttons
**Old**: `ft.ElevatedButton(text="Click", ...)`  
**New**: `ft.Button("Click", ...)`  
- First parameter is now the text (no `text=` keyword)

### 4. Borders
**Old**: `ft.border.all(1, color)`  
**New**: `ft.Border.all(1, color)`

### 5. Margins
**Old**: `ft.margin.only(bottom=20)`  
**New**: `ft.Margin(left=0, top=0, right=0, bottom=20)`

### 6. App Runner
**Old**: `ft.app(target=main)`  
**New**: `ft.run(main)`  
- No `target=` keyword needed

## Summary

All changes follow a pattern:
- Lowercase module names → Capitalized class names
- Keyword arguments for text → Positional arguments
- More explicit constructor calls (Margin, Border)

## Compatibility

These changes are required for:
- Flet >= 0.80.0
- Python 3.9+
- Playwright 1.40+
