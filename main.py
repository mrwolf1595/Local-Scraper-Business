"""Main application with Flet UI"""

import flet as ft
from flet import Colors
import asyncio
import pandas as pd
from datetime import datetime
from pathlib import Path
from scraper import GoogleMapsScraper
from config import *


class ScraperApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.scraper = GoogleMapsScraper()
        self.data_rows = []
        self.is_arabic = True  # Default to Arabic
        
        # Translations
        self.translations = {
            'ar': {
                'title': 'مستخرج بيانات الأعمال',
                'subtitle': 'استخراج بيانات الأعمال مع إزالة التكرار التلقائي',
                'business_tag': 'نوع النشاط',
                'business_hint': 'مثال: مكتب عقارات، مكتب محاماة، وكالة سيارات',
                'region': 'المنطقة',
                'region_hint': 'مثال: مكة',
                'city': 'المدينة',
                'city_hint': 'مثال: جدة',
                'district': 'الحي (اختياري)',
                'district_hint': 'مثال: النزهة، الروضة',
                'start_search': 'بدء البحث',
                'stop': 'إيقاف',
                'export': 'تصدير إلى Excel',
                'ready': 'جاهز للبحث',
                'extracted_data': 'البيانات المستخرجة',
                'status_log': 'سجل الحالة',
                'col_num': '#',
                'col_name': 'اسم النشاط',
                'col_phone': 'الهاتف',
                'col_address': 'العنوان',
                'col_location': 'الموقع',
                'col_website': 'الموقع الإلكتروني',
                'col_email': 'البريد الإلكتروني',
                'view_map': 'عرض الخريطة',
                'language': 'English',
                'about': 'معلومات عنا',
            },
            'en': {
                'title': 'Business Data Extractor Pro',
                'subtitle': 'Extract business data with Emails & Socials',
                'business_tag': 'Business Tag',
                'business_hint': 'e.g., Real Estate Office, Law Firm, Car Dealership',
                'region': 'Region',
                'region_hint': 'e.g., Makkah',
                'city': 'City',
                'city_hint': 'e.g., Jeddah',
                'district': 'District (Optional)',
                'district_hint': 'e.g., Al-Nazlah, Al-Rawdah',
                'start_search': 'Start Search',
                'stop': 'Stop',
                'export': 'Export to Excel',
                'ready': 'Ready to search',
                'extracted_data': 'Extracted Data',
                'status_log': 'Status Log',
                'col_num': '#',
                'col_name': 'Business Name',
                'col_phone': 'Phone',
                'col_address': 'Address',
                'col_location': 'Location',
                'col_website': 'Website',
                'col_email': 'Email',
                'view_map': 'View Map',
                'language': 'عربي',
                'about': 'About Agency',
            }
        }
        
        # Configure page
        self.page.title = APP_TITLE
        self.page.window_width = WINDOW_WIDTH
        self.page.window_height = WINDOW_HEIGHT
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.rtl = True  # Right-to-left for Arabic
        self.page.scroll = ft.ScrollMode.AUTO  # Enable scrolling
        self.page.fonts = {
            "Roboto": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf",
        }
        self.page.theme = ft.Theme(font_family="Roboto")
        
        # UI Components
        self.language_button = None
        self.about_button = None
        self.header_title = None
        self.header_subtitle = None
        self.business_tag_field = None
        self.region_field = None
        self.city_field = None
        self.district_field = None
        self.start_button = None
        self.stop_button = None
        self.export_button = None
        self.status_text = None
        self.log_container = None
        self.data_table = None
        self.data_table_title = None
        self.log_title = None
        
        self.build_ui()
        
    def get_text(self, key):
        """Get translated text"""
        lang = 'ar' if self.is_arabic else 'en'
        return self.translations[lang][key]
    
    def toggle_language(self, e):
        """Toggle between Arabic and English"""
        self.is_arabic = not self.is_arabic
        self.page.rtl = self.is_arabic
        self.update_ui_language()
        self.page.update()
    
    def update_ui_language(self):
        """Update all UI text to current language"""
        self.language_button.text = self.get_text('language')
        self.about_button.text = self.get_text('about')
        self.header_title.value = self.get_text('title')
        self.header_subtitle.value = self.get_text('subtitle')
        self.business_tag_field.label = self.get_text('business_tag')
        self.business_tag_field.hint_text = self.get_text('business_hint')
        self.region_field.label = self.get_text('region')
        self.region_field.hint_text = self.get_text('region_hint')
        self.city_field.label = self.get_text('city')
        self.city_field.hint_text = self.get_text('city_hint')
        self.district_field.label = self.get_text('district')
        self.district_field.hint_text = self.get_text('district_hint')
        self.start_button.text = self.get_text('start_search')
        self.stop_button.text = self.get_text('stop')
        self.export_button.text = self.get_text('export')
        self.status_text.value = self.get_text('ready')
        self.data_table_title.value = self.get_text('extracted_data')
        self.log_title.value = self.get_text('status_log')
        
        # Update table headers
        self.data_table.columns = [
            ft.DataColumn(ft.Text(self.get_text('col_num'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_name'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_phone'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_address'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_website'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_email'), weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text(self.get_text('col_location'), weight=ft.FontWeight.BOLD)),
        ]
        
    def build_ui(self):
        """Build the UI components"""
        
        # Language toggle button
        self.language_button = ft.Button(
            self.get_text('language'),
            icon=ft.Icons.LANGUAGE,
            on_click=self.toggle_language,
            style=ft.ButtonStyle(
                color=Colors.BLUE_700,
            ),
        )
        
        self.about_button = ft.Button(
            self.get_text('about'),
            icon=ft.Icons.INFO,
            on_click=self.show_about_dialog,
            style=ft.ButtonStyle(color=Colors.BLUE_700),
        )
        
        # Header
        self.header_title = ft.Text(
            self.get_text('title'),
            size=32,
            weight=ft.FontWeight.BOLD,
            color=Colors.BLUE_700
        )
        
        self.header_subtitle = ft.Text(
            self.get_text('subtitle'),
            size=14,
            color=Colors.GREY_700
        )
        
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        self.header_title,
                        self.header_subtitle,
                    ], expand=True),
                    ft.Row([
                        self.about_button,
                        self.language_button,
                    ]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            margin=ft.Margin(left=0, top=0, right=0, bottom=20)
        )
        
        # Input fields with enhanced styling
        self.business_tag_field = ft.TextField(
            label=self.get_text('business_tag'),
            hint_text=self.get_text('business_hint'),
            prefix_icon=ft.Icons.BUSINESS_CENTER,
            border_color=Colors.BLUE_400,
            focused_border_color=Colors.BLUE_700,
            expand=True,
        )
        
        self.region_field = ft.TextField(
            label=self.get_text('region'),
            hint_text=self.get_text('region_hint'),
            prefix_icon=ft.Icons.LOCATION_CITY,
            border_color=Colors.BLUE_400,
            focused_border_color=Colors.BLUE_700,
            expand=1,
        )
        
        self.city_field = ft.TextField(
            label=self.get_text('city'),
            hint_text=self.get_text('city_hint'),
            prefix_icon=ft.Icons.LOCATION_ON,
            border_color=Colors.BLUE_400,
            focused_border_color=Colors.BLUE_700,
            expand=1,
        )
        
        self.district_field = ft.TextField(
            label=self.get_text('district'),
            hint_text=self.get_text('district_hint'),
            prefix_icon=ft.Icons.MAP,
            border_color=Colors.GREY_400,
            focused_border_color=Colors.BLUE_700,
            expand=1,
        )
        
        # Organize inputs in card-style containers
        inputs_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SETTINGS, color=Colors.BLUE_600, size=20),
                        ft.Text(
                            self.get_text('business_tag') if not self.is_arabic else "إعدادات البحث",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=Colors.BLUE_700,
                        ),
                    ], spacing=8),
                    ft.Divider(height=1, color=Colors.GREY_300),
                    self.business_tag_field,
                    ft.Row([
                        self.region_field,
                        self.city_field,
                        self.district_field,
                    ], spacing=10),
                ], spacing=15, tight=True),
                padding=20,
            ),
            elevation=2,
        )
        
        # Control buttons
        self.start_button = ft.Button(
            self.get_text('start_search'),
            icon=ft.Icons.SEARCH,
            on_click=self.start_search,
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor=Colors.GREEN_600,
            ),
            height=50,
        )
        
        self.stop_button = ft.Button(
            self.get_text('stop'),
            icon=ft.Icons.STOP,
            on_click=self.stop_search,
            disabled=True,
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor=Colors.RED_600,
            ),
            height=50,
        )
        
        self.export_button = ft.Button(
            self.get_text('export'),
            icon=ft.Icons.DOWNLOAD,
            on_click=self.export_data,
            disabled=True,
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor=Colors.BLUE_600,
            ),
            height=50,
        )
        
        buttons_row = ft.Row([
            self.start_button,
            self.stop_button,
            self.export_button,
        ], spacing=10)
        
        # Status text with enhanced styling
        self.status_text = ft.Text(
            self.get_text('ready'),
            size=14,
            weight=ft.FontWeight.W_500,
            color=Colors.GREY_800,
        )
        
        status_card = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=Colors.BLUE_600, size=18),
                    self.status_text,
                ], spacing=8, tight=True),
                padding=12,
            ),
            elevation=1,
        )
        
        # Data table
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(self.get_text('col_num'), weight=ft.FontWeight.BOLD, size=12), numeric=True),
                ft.DataColumn(ft.Text(self.get_text('col_name'), weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text(self.get_text('col_phone'), weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text(self.get_text('col_address'), weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text(self.get_text('col_website'), weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text(self.get_text('col_email'), weight=ft.FontWeight.BOLD, size=12)),
                ft.DataColumn(ft.Text(self.get_text('col_location'), weight=ft.FontWeight.BOLD, size=12)),
            ],
            rows=[],
            border=ft.Border.all(1, Colors.GREY_300),
            border_radius=10,
            heading_row_color=Colors.BLUE_50,
            horizontal_lines=ft.BorderSide(1, Colors.GREY_200),
            column_spacing=20,
            heading_row_height=40,
            data_row_min_height=35,
            data_row_max_height=60,
        )
        
        self.data_table_title = ft.Text(
            self.get_text('extracted_data'),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=Colors.BLUE_700,
        )
        
        data_table_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TABLE_CHART, color=Colors.BLUE_600, size=18),
                        self.data_table_title,
                    ], spacing=8),
                    ft.Divider(height=1, color=Colors.GREY_300),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([self.data_table], scroll=ft.ScrollMode.ALWAYS),
                        ], scroll=ft.ScrollMode.ALWAYS),
                        bgcolor=Colors.WHITE,
                        border_radius=8,
                        padding=10,
                        height=350,
                    ),
                ], spacing=10, tight=True),
                padding=15,
            ),
            elevation=2,
        )
        
        # Log container
        self.log_container = ft.ListView(
            spacing=5,
            padding=10,
            auto_scroll=True,
            height=150,
        )
        
        self.log_title = ft.Text(
            self.get_text('status_log'),
            size=16,
            weight=ft.FontWeight.BOLD,
            color=Colors.BLUE_700,
        )
        
        log_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.NOTES, color=Colors.BLUE_600, size=18),
                        self.log_title,
                    ], spacing=8),
                    ft.Divider(height=1, color=Colors.GREY_300),
                    ft.Container(
                        content=self.log_container,
                        bgcolor=Colors.GREY_50,
                        border_radius=8,
                        height=150,
                    ),
                ], spacing=10, tight=True),
                padding=15,
            ),
            elevation=2,
        )
        
        # Main layout
        self.page.add(
            header,
            ft.Divider(height=1, color=Colors.GREY_300),
            ft.Container(height=10),
            inputs_card,
            ft.Container(height=10),
            buttons_row,
            ft.Container(height=10),
            status_card,
            ft.Container(height=10),
            data_table_card,
            ft.Container(height=10),
            log_card,
            ft.Container(height=10),
        )
        
    def show_about_dialog(self, e):
        """Show about dialog"""
        dlg = ft.AlertDialog(
            title=ft.Text(self.get_text('about')),
            content=ft.Column([
                ft.Text("Business Data Extractor & Marketing Suite", weight=ft.FontWeight.BOLD),
                ft.Text("Empowering businesses with high-quality, actionable data for successful marketing campaigns."),
                ft.Divider(),
                ft.Text("Version: 2.5.0 (Enterprise Edition)"),
                ft.Text("Developed for Professional Use."),
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.page.close_dialog()),
            ],
        )
        self.page.open_dialog(dlg)

    def add_log(self, message: str):
        """Add a log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = ft.Text(
            f"[{timestamp}] {message}",
            size=12,
            color=Colors.GREY_800,
        )
        self.log_container.controls.append(log_entry)
        self.page.update()
        
    def update_status(self, message: str):
        """Update status text"""
        self.status_text.value = message
        self.add_log(message)
        self.page.update()
        
    def add_data_row(self, data: dict):
        """Add a row to the data table"""
        row_num = len(self.data_rows) + 1
        self.data_rows.append(data)
        
        # Create location link
        location_text = self.get_text('view_map') if data.get('latitude') and data.get('longitude') else "N/A"
        
        self.data_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(row_num), size=12)),
                    ft.DataCell(ft.Text(data.get('name', 'N/A'), size=11, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(ft.Text(data.get('phone', 'N/A'), size=11)),
                    ft.DataCell(ft.Text(data.get('address', 'N/A'), size=11, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(ft.Text(data.get('website', 'N/A'), size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(ft.Text(data.get('emails', 'N/A'), size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                    ft.DataCell(
                        ft.TextButton(
                            location_text,
                            on_click=lambda e, url=data.get('url'): self.page.launch_url(url) if url else None,
                        ) if data.get('url') else ft.Text("N/A", size=11)
                    ),
                ]
            )
        )
        self.page.update()
        
    def on_search_complete(self):
        """Called when search completes"""
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.export_button.disabled = len(self.data_rows) == 0
        self.page.update()
        
    async def run_search(self):
        """Run the search asynchronously"""
        try:
            # Setup callbacks
            self.scraper.on_status_update = self.update_status
            self.scraper.on_data_found = self.add_data_row
            self.scraper.on_complete = self.on_search_complete
            
            # Run search
            await self.scraper.search(
                self.business_tag_field.value,
                self.region_field.value,
                self.city_field.value,
                self.district_field.value or ""
            )
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.on_search_complete()
            
    def start_search(self, e):
        """Start button click handler"""
        # Validate inputs
        if not self.business_tag_field.value or not self.region_field.value or not self.city_field.value:
            msg = "يرجى ملء جميع الحقول الإلزامية" if self.is_arabic else "Please fill in all required fields"
            self.update_status(msg)
            return
        
        # Show what will be searched
        district_text = f" - {self.district_field.value}" if self.district_field.value else ""
        search_info = f"{self.business_tag_field.value} | {self.city_field.value}{district_text}, {self.region_field.value}"
        self.update_status(search_info)
            
        # Clear previous data
        self.data_rows.clear()
        self.data_table.rows.clear()
        self.log_container.controls.clear()
        
        # Update UI
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.export_button.disabled = True
        self.page.update()
        
        # Run search in background
        asyncio.create_task(self.run_search())
        
    def stop_search(self, e):
        """Stop button click handler"""
        self.scraper.stop()
        self.update_status("Search stopped by user")
        self.on_search_complete()
        
    def export_data(self, e):
        """Export data to Excel"""
        if not self.data_rows:
            self.update_status("No data to export")
            return
            
        try:
            # Create output directory
            output_dir = Path(OUTPUT_DIR)
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_maps_export_{timestamp}.xlsx"
            filepath = output_dir / filename
            
            # Create DataFrame
            df = pd.DataFrame(self.data_rows)
            
            # Select and rename columns
            columns_map = {
                'name': 'Business Name',
                'phone': 'Phone',
                'address': 'Address',
                'website': 'Website',
                'emails': 'Emails',
                'socials': 'Social Media',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
                'url': 'Google Maps URL'
            }
            
            df = df[[col for col in columns_map.keys() if col in df.columns]]
            df.rename(columns=columns_map, inplace=True)
            
            # Export to Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            self.update_status(f"Exported to: {filepath}")
            
            # Open file location
            import subprocess
            subprocess.Popen(f'explorer /select,"{filepath.absolute()}"')
            
        except Exception as ex:
            self.update_status(f"Export failed: {str(ex)}")


def main(page: ft.Page):
    app = ScraperApp(page)


if __name__ == "__main__":
    ft.run(main)
