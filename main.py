"""Enterprise Business Data Extraction Platform - Premium UI for Flet 0.80+"""

import flet as ft
from flet import Colors, Icons
import asyncio
import pandas as pd
from datetime import datetime
from pathlib import Path
from scraper import GoogleMapsScraper
from config import *

# --- Premium Enterprise Theme Constants ---
class AppTheme:
    PRIMARY = "#4F46E5"
    PRIMARY_LIGHT = "#818CF8"
    PRIMARY_DARK = "#3730A3"
    ACCENT = "#06B6D4"
    ACCENT_LIGHT = "#67E8F9"
    SUCCESS = "#10B981"
    SUCCESS_LIGHT = "#34D399"
    ERROR = "#EF4444"
    ERROR_LIGHT = "#F87171"
    WARNING = "#F59E0B"
    WARNING_LIGHT = "#FBBF24"
    BACKGROUND = "#0F172A"
    SURFACE = "#1E293B"
    SURFACE_LIGHT = "#334155"
    CARD = "#1E293B"
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    BORDER = "#334155"

class ScraperApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.scraper = GoogleMapsScraper()
        self.data_rows = []
        self.is_arabic = True
        self.search_start_time = None
        
        self.stats = {'total': 0, 'phones': 0, 'emails': 0, 'websites': 0}
        
        self.translations = {
            'ar': {
                'app_title': 'منصة استخراج البيانات',
                'app_subtitle': 'نظام تسويق الشركات الاحترافي',
                'settings': 'إعدادات الحملة',
                'business_tag': 'نوع النشاط التجاري',
                'business_hint': 'مثال: شركات مقاولات، عيادات اسنان',
                'region': 'المنطقة / المحافظة',
                'region_hint': 'مثال: الرياض، جدة',
                'city': 'المدينة',
                'city_hint': 'مثال: الخرج، مكة',
                'district': 'الحي (اختياري)',
                'district_hint': 'مثال: النسيم، العزيزية',
                'start_search': 'بدء استخراج البيانات',
                'stop': 'إيقاف العملية',
                'export': 'تصدير إلى Excel',
                'status_ready': 'النظام جاهز - في انتظار بدء الحملة',
                'status_running': 'جارٍ استخراج البيانات...',
                'status_stopped': 'تم إيقاف العملية',
                'results_title': 'نتائج الاستخراج المباشرة',
                'stats_total': 'إجمالي الشركات',
                'stats_phones': 'أرقام التواصل',
                'stats_emails': 'البريد الإلكتروني',
                'stats_websites': 'المواقع الإلكترونية',
                'col_num': '#',
                'col_name': 'اسم الشركة',
                'col_phone': 'رقم التواصل',
                'col_address': 'العنوان',
                'col_website': 'الموقع الإلكتروني',
                'col_email': 'البريد الإلكتروني',
                'col_location': 'الخريطة',
                'view_map': 'عرض الخريطة',
                'language': 'English',
                'about': 'عن النظام',
                'about_title': 'Business Extractor Enterprise',
                'about_desc': 'منصة متقدمة لاستخراج بيانات العملاء المحتملين من خرائط جوجل.',
                'validation_error': 'يرجى إكمال جميع الحقول المطلوبة',
                'clear_data': 'مسح البيانات',
                'version': 'الإصدار 3.0 Enterprise',
                'search_query': 'البحث عن:'
            },
            'en': {
                'app_title': 'Data Extraction Platform',
                'app_subtitle': 'Enterprise Marketing Suite',
                'settings': 'Campaign Settings',
                'business_tag': 'Business Type',
                'business_hint': 'e.g. Construction Companies, Dental Clinics',
                'region': 'Region / Province',
                'region_hint': 'e.g. Riyadh, Jeddah',
                'city': 'City',
                'city_hint': 'e.g. Al-Kharj, Makkah',
                'district': 'District (Optional)',
                'district_hint': 'e.g. Al-Naseem, Al-Aziziyah',
                'start_search': 'Start Data Extraction',
                'stop': 'Stop Process',
                'export': 'Export to Excel',
                'status_ready': 'System Ready - Awaiting Campaign',
                'status_running': 'Data Extraction in Progress...',
                'status_stopped': 'Process Stopped',
                'results_title': 'Live Extraction Results',
                'stats_total': 'Total Companies',
                'stats_phones': 'Phone Numbers',
                'stats_emails': 'Email Addresses',
                'stats_websites': 'Websites Found',
                'col_num': '#',
                'col_name': 'Company Name',
                'col_phone': 'Phone Number',
                'col_address': 'Address',
                'col_website': 'Website',
                'col_email': 'Email',
                'col_location': 'Map',
                'view_map': 'View Map',
                'language': 'عربي',
                'about': 'About',
                'about_title': 'Business Extractor Enterprise',
                'about_desc': 'Advanced lead extraction from Google Maps.',
                'validation_error': 'Please complete all required fields',
                'clear_data': 'Clear Data',
                'version': 'Version 3.0 Enterprise',
                'search_query': 'Searching:'
            }
        }
        
        # Configure page
        self.page.title = APP_TITLE
        self.page.window.width = 1400
        self.page.window.height = 900
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = AppTheme.BACKGROUND
        self.page.padding = 0
        self.page.rtl = True
        
        self.page.fonts = {"Cairo": "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo-Bold.ttf"}
        self.page.theme = ft.Theme(font_family="Cairo", color_scheme_seed=AppTheme.PRIMARY)
        
        # UI Components
        self.txt_business = None
        self.txt_region = None
        self.txt_city = None
        self.txt_district = None
        self.btn_start = None
        self.btn_stop = None
        self.btn_export = None
        self.btn_lang = None
        self.btn_about = None
        self.btn_clear = None
        self.lbl_status = None
        self.status_indicator = None
        self.log_view = None
        self.data_table = None
        self.progress_ring = None
        self.stat_total_val = None
        self.stat_phone_val = None
        self.stat_email_val = None
        self.stat_website_val = None
        self.sidebar_title = None
        self.sidebar_subtitle = None
        self.results_title_text = None
        self.empty_state = None
        
        self.build_ui()
        
    def get_text(self, key):
        lang = 'ar' if self.is_arabic else 'en'
        return self.translations[lang].get(key, key)
    
    def toggle_language(self, e):
        self.is_arabic = not self.is_arabic
        self.page.rtl = self.is_arabic
        self.update_ui_language()
        self.page.update()
        
    def update_ui_language(self):
        self.sidebar_title.value = self.get_text('app_title')
        self.sidebar_subtitle.value = self.get_text('app_subtitle')
        self.txt_business.label = self.get_text('business_tag')
        self.txt_business.hint_text = self.get_text('business_hint')
        self.txt_region.label = self.get_text('region')
        self.txt_region.hint_text = self.get_text('region_hint')
        self.txt_city.label = self.get_text('city')
        self.txt_city.hint_text = self.get_text('city_hint')
        self.txt_district.label = self.get_text('district')
        self.txt_district.hint_text = self.get_text('district_hint')
        self.btn_start.content.controls[1].value = self.get_text('start_search')
        self.btn_stop.content.controls[1].value = self.get_text('stop')
        self.btn_export.content.controls[1].value = self.get_text('export')
        self.btn_lang.content.controls[1].value = self.get_text('language')
        self.lbl_status.value = self.get_text('status_ready')
        self.results_title_text.value = self.get_text('results_title')
        
        cols = self.data_table.columns
        cols[0].label.value = self.get_text('col_num')
        cols[1].label.value = self.get_text('col_name')
        cols[2].label.value = self.get_text('col_phone')
        cols[3].label.value = self.get_text('col_address')
        cols[4].label.value = self.get_text('col_website')
        cols[5].label.value = self.get_text('col_email')
        cols[6].label.value = self.get_text('col_location')

    def _create_button(self, label, icon, bgcolor, on_click, width=290, disabled=False):
        """Create a styled button compatible with Flet 0.80+"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=Colors.WHITE, size=18),
                ft.Text(label, color=Colors.WHITE, weight=ft.FontWeight.W_600, size=14)
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=bgcolor if not disabled else Colors.with_opacity(0.3, bgcolor),
            padding=ft.Padding(20, 16, 20, 16),
            border_radius=12,
            width=width,
            on_click=on_click if not disabled else None,
            disabled=disabled,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

    def build_sidebar(self):
        # Logo
        logo_icon = ft.Container(
            content=ft.Icon(Icons.ANALYTICS_ROUNDED, size=32, color=Colors.WHITE),
            width=60,
            height=60,
            border_radius=15,
            bgcolor=AppTheme.PRIMARY,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=20, color=Colors.with_opacity(0.3, AppTheme.PRIMARY), offset=ft.Offset(0, 4))
        )
        
        self.sidebar_title = ft.Text(self.get_text('app_title'), size=20, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        self.sidebar_subtitle = ft.Text(self.get_text('app_subtitle'), size=12, color=AppTheme.TEXT_SECONDARY)
        
        branding = ft.Container(
            content=ft.Column([logo_icon, ft.Container(height=10), self.sidebar_title, self.sidebar_subtitle], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(0, 25, 0, 20)
        )
        
        settings_header = ft.Container(
            content=ft.Row([ft.Icon(Icons.TUNE_ROUNDED, color=AppTheme.TEXT_SECONDARY, size=18), ft.Text(self.get_text('settings'), weight=ft.FontWeight.W_600, color=AppTheme.TEXT_SECONDARY, size=13)], spacing=8),
            padding=ft.Padding(0, 0, 0, 12)
        )
        
        # Input Fields
        input_style = dict(border_radius=12, border_color=AppTheme.BORDER, focused_border_color=AppTheme.PRIMARY_LIGHT, bgcolor=AppTheme.SURFACE, text_size=14, content_padding=ft.Padding(15, 18, 15, 18), cursor_color=AppTheme.PRIMARY_LIGHT, label_style=ft.TextStyle(color=AppTheme.TEXT_SECONDARY), hint_style=ft.TextStyle(color=AppTheme.TEXT_MUTED), text_style=ft.TextStyle(color=AppTheme.TEXT_PRIMARY))
        
        self.txt_business = ft.TextField(label=self.get_text('business_tag'), hint_text=self.get_text('business_hint'), prefix_icon=Icons.SEARCH_ROUNDED, **input_style)
        self.txt_region = ft.TextField(label=self.get_text('region'), hint_text=self.get_text('region_hint'), prefix_icon=Icons.PUBLIC_ROUNDED, **input_style)
        self.txt_city = ft.TextField(label=self.get_text('city'), hint_text=self.get_text('city_hint'), prefix_icon=Icons.LOCATION_CITY_ROUNDED, **input_style)
        self.txt_district = ft.TextField(label=self.get_text('district'), hint_text=self.get_text('district_hint'), prefix_icon=Icons.PLACE_ROUNDED, **input_style)
        
        # Buttons
        self.btn_start = self._create_button(self.get_text('start_search'), Icons.ROCKET_LAUNCH_ROUNDED, AppTheme.PRIMARY, self.start_search)
        self.btn_stop = self._create_button(self.get_text('stop'), Icons.STOP_CIRCLE_ROUNDED, AppTheme.ERROR, self.stop_search, disabled=True)
        self.btn_export = self._create_button(self.get_text('export'), Icons.DOWNLOAD_ROUNDED, AppTheme.SUCCESS, self.export_data, disabled=True)
        
        # Status
        self.status_indicator = ft.Container(width=10, height=10, border_radius=5, bgcolor=AppTheme.SUCCESS)
        self.lbl_status = ft.Text(self.get_text('status_ready'), size=12, color=AppTheme.TEXT_SECONDARY, weight=ft.FontWeight.W_500, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
        self.progress_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=AppTheme.PRIMARY_LIGHT, visible=False)
        status_row = ft.Container(content=ft.Row([self.status_indicator, self.progress_ring, self.lbl_status], spacing=10), padding=ft.Padding(0, 10, 0, 10))
        
        # Log
        self.log_view = ft.ListView(expand=True, spacing=3, auto_scroll=True, padding=12)
        log_container = ft.Container(content=self.log_view, bgcolor=AppTheme.BACKGROUND, border_radius=12, height=140, border=ft.border.all(1, AppTheme.BORDER))

        return ft.Container(
            content=ft.Column([
                branding,
                ft.Container(height=1, bgcolor=AppTheme.BORDER, margin=ft.Margin(0, 5, 0, 5)),
                settings_header,
                self.txt_business,
                self.txt_region,
                self.txt_city,
                self.txt_district,
                ft.Container(height=15),
                self.btn_start,
                ft.Container(height=8),
                self.btn_stop,
                self.btn_export,
                ft.Container(height=15),
                ft.Container(height=1, bgcolor=AppTheme.BORDER, margin=ft.Margin(0, 5, 0, 5)),
                status_row,
                log_container,
            ], scroll=ft.ScrollMode.AUTO, spacing=8),
            width=340,
            bgcolor=AppTheme.SURFACE,
            padding=20,
            border=ft.border.only(right=ft.BorderSide(1, AppTheme.BORDER)) if not self.is_arabic else ft.border.only(left=ft.BorderSide(1, AppTheme.BORDER))
        )

    def create_stat_card(self, title, value_ref, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=color, size=22),
                    width=48, height=48,
                    bgcolor=Colors.with_opacity(0.15, color),
                    border_radius=12,
                ),
                ft.Container(width=12),
                ft.Column([ft.Text(title, size=12, color=AppTheme.TEXT_MUTED, weight=ft.FontWeight.W_500), value_ref], spacing=2)
            ]),
            bgcolor=AppTheme.CARD,
            padding=ft.Padding(16, 14, 16, 14),
            border_radius=14,
            border=ft.border.all(1, AppTheme.BORDER),
            expand=True,
        )

    def build_main_content(self):
        self.stat_total_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        self.stat_phone_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        self.stat_email_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        self.stat_website_val = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        
        stats_row = ft.Row([
            self.create_stat_card(self.get_text('stats_total'), self.stat_total_val, Icons.BUSINESS_ROUNDED, AppTheme.PRIMARY_LIGHT),
            self.create_stat_card(self.get_text('stats_phones'), self.stat_phone_val, Icons.PHONE_ROUNDED, AppTheme.ACCENT),
            self.create_stat_card(self.get_text('stats_emails'), self.stat_email_val, Icons.EMAIL_ROUNDED, AppTheme.WARNING),
            self.create_stat_card(self.get_text('stats_websites'), self.stat_website_val, Icons.LANGUAGE_ROUNDED, AppTheme.SUCCESS),
        ], spacing=16)
        
        col_style = ft.TextStyle(weight=ft.FontWeight.W_600, size=13, color=AppTheme.TEXT_SECONDARY)
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(self.get_text('col_num'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_name'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_phone'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_address'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_website'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_email'), style=col_style)),
                ft.DataColumn(ft.Text(self.get_text('col_location'), style=col_style)),
            ],
            rows=[],
            border=ft.border.all(1, AppTheme.BORDER),
            vertical_lines=ft.BorderSide(1, AppTheme.BACKGROUND),
            horizontal_lines=ft.BorderSide(1, AppTheme.BORDER),
            heading_row_color=AppTheme.SURFACE_LIGHT,
            heading_row_height=55,
            data_row_min_height=55,
            expand=True,
            column_spacing=20,
        )
        
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(Icons.SEARCH_OFF_ROUNDED, size=64, color=AppTheme.TEXT_MUTED),
                ft.Text("ابدأ حملة البحث لاستخراج البيانات" if self.is_arabic else "Start a campaign", color=AppTheme.TEXT_MUTED, size=14)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            expand=True, visible=True
        )
        
        table_container = ft.Container(
            content=ft.Column([ft.Container(content=self.data_table, expand=True), self.empty_state], scroll=ft.ScrollMode.AUTO),
            bgcolor=AppTheme.CARD, border_radius=16, border=ft.border.all(1, AppTheme.BORDER), padding=0, expand=True,
        )
        
        self.results_title_text = ft.Text(self.get_text('results_title'), size=18, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY)
        
        self.btn_lang = ft.Container(
            content=ft.Row([ft.Icon(Icons.TRANSLATE_ROUNDED, color=AppTheme.TEXT_SECONDARY, size=16), ft.Text(self.get_text('language'), color=AppTheme.TEXT_SECONDARY, size=13)], spacing=8),
            on_click=self.toggle_language, padding=ft.Padding(12, 8, 12, 8), border_radius=8,
        )
        
        self.btn_about = ft.IconButton(icon=Icons.INFO_OUTLINE_ROUNDED, tooltip=self.get_text('about'), on_click=self.show_about_dialog, icon_color=AppTheme.TEXT_MUTED)
        self.btn_clear = ft.IconButton(icon=Icons.DELETE_SWEEP_ROUNDED, icon_color=AppTheme.TEXT_MUTED, icon_size=20, tooltip=self.get_text('clear_data'), on_click=self.clear_data)

        top_bar = ft.Container(
            content=ft.Row([
                ft.Row([ft.Container(width=4, height=24, border_radius=2, bgcolor=AppTheme.PRIMARY), ft.Container(width=12), self.results_title_text]),
                ft.Row([self.btn_clear, self.btn_lang, self.btn_about], spacing=4)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(0, 0, 0, 16)
        )

        return ft.Container(
            content=ft.Column([top_bar, stats_row, ft.Container(height=16), table_container], spacing=0, expand=True),
            padding=24, expand=True, bgcolor=AppTheme.BACKGROUND
        )

    def build_ui(self):
        self.sidebar = self.build_sidebar()
        self.main_content = self.build_main_content()
        self.page.add(ft.Row([self.sidebar, self.main_content], expand=True, spacing=0))

    def show_about_dialog(self, e):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Container(content=ft.Icon(Icons.ANALYTICS_ROUNDED, color=Colors.WHITE, size=24), width=44, height=44, border_radius=12, bgcolor=AppTheme.PRIMARY),
                ft.Container(width=12),
                ft.Column([ft.Text(self.get_text('about_title'), weight=ft.FontWeight.BOLD, size=16), ft.Text(self.get_text('version'), size=11, color=AppTheme.TEXT_MUTED)], spacing=2)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(self.get_text('about_desc'), size=14, color=AppTheme.TEXT_SECONDARY),
                    ft.Container(height=16),
                    ft.Row([ft.Text("© 2024 Enterprise Edition", size=11, color=AppTheme.TEXT_MUTED)], alignment=ft.MainAxisAlignment.CENTER)
                ], tight=True),
                width=400, padding=ft.Padding(0, 8, 0, 0)
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: self.page.close(dlg), style=ft.ButtonStyle(color=AppTheme.PRIMARY_LIGHT))],
            bgcolor=AppTheme.SURFACE, shape=ft.RoundedRectangleBorder(radius=16),
        )
        self.page.open(dlg)

    def add_log(self, message: str, is_error=False, is_success=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = AppTheme.ERROR_LIGHT if is_error else (AppTheme.SUCCESS_LIGHT if is_success else AppTheme.TEXT_MUTED)
        icon = Icons.ERROR_OUTLINE_ROUNDED if is_error else (Icons.CHECK_CIRCLE_OUTLINE_ROUNDED if is_success else Icons.CHEVRON_RIGHT_ROUNDED)
        
        log_entry = ft.Container(content=ft.Row([ft.Icon(icon, size=12, color=color), ft.Text(timestamp, size=10, color=AppTheme.TEXT_MUTED), ft.Text(message, size=11, color=color, selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, expand=True)], spacing=8))
        self.log_view.controls.append(log_entry)
        if len(self.log_view.controls) > 50:
            self.log_view.controls.pop(0)
        self.page.update()

    def update_status(self, message: str, is_running=False):
        self.lbl_status.value = message
        if is_running:
            self.status_indicator.bgcolor = AppTheme.WARNING
            self.progress_ring.visible = True
            self.status_indicator.visible = False
        else:
            self.status_indicator.bgcolor = AppTheme.SUCCESS
            self.progress_ring.visible = False
            self.status_indicator.visible = True
        self.add_log(message)
        self.page.update()

    def update_stats(self):
        self.stat_total_val.value = str(self.stats['total'])
        self.stat_phone_val.value = str(self.stats['phones'])
        self.stat_email_val.value = str(self.stats['emails'])
        self.stat_website_val.value = str(self.stats['websites'])
        self.empty_state.visible = self.stats['total'] == 0
        self.page.update()

    def add_data_row(self, data: dict):
        row_num = len(self.data_rows) + 1
        self.data_rows.append(data)
        
        self.stats['total'] += 1
        if data.get('phone') and len(str(data.get('phone', ''))) > 3 and data.get('phone') != 'N/A':
            self.stats['phones'] += 1
        if data.get('emails') and len(str(data.get('emails', ''))) > 3 and data.get('emails') != 'N/A':
            self.stats['emails'] += 1
        if data.get('website') and data.get('website') != 'N/A':
            self.stats['websites'] += 1
        self.update_stats()
        
        name_cell = ft.Container(content=ft.Text(data.get('name', ''), weight=ft.FontWeight.W_600, size=13, color=AppTheme.TEXT_PRIMARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS), width=160)
        phone_text = data.get('phone', 'N/A')
        phone_cell = ft.Text(phone_text, size=12, color=AppTheme.ACCENT if phone_text != 'N/A' else AppTheme.TEXT_MUTED, selectable=True)
        address_cell = ft.Container(content=ft.Text(data.get('address', ''), size=12, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS, color=AppTheme.TEXT_SECONDARY), width=180)
        
        website_url = data.get('website')
        website_cell = ft.IconButton(icon=Icons.OPEN_IN_NEW_ROUNDED, icon_color=AppTheme.PRIMARY_LIGHT, icon_size=18, tooltip=website_url, url=website_url) if website_url and website_url != 'N/A' else ft.Icon(Icons.LINK_OFF_ROUNDED, color=AppTheme.TEXT_MUTED, size=18)
        
        email_text = data.get('emails', 'N/A')
        email_cell = ft.Container(content=ft.Text(email_text or 'N/A', size=12, color=AppTheme.WARNING_LIGHT if email_text and email_text != 'N/A' else AppTheme.TEXT_MUTED, selectable=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), width=150)
        
        map_url = data.get('url')
        map_cell = ft.IconButton(icon=Icons.MAP_ROUNDED, icon_color=AppTheme.SUCCESS_LIGHT, icon_size=18, tooltip=self.get_text('view_map'), on_click=lambda e, url=map_url: self.page.launch_url(url)) if map_url else ft.Container()
        
        row_color = AppTheme.SURFACE if row_num % 2 == 0 else AppTheme.CARD
        
        self.data_table.rows.append(ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(row_num), size=12, weight=ft.FontWeight.W_600, color=AppTheme.TEXT_MUTED)),
                ft.DataCell(name_cell), ft.DataCell(phone_cell), ft.DataCell(address_cell),
                ft.DataCell(website_cell), ft.DataCell(email_cell), ft.DataCell(map_cell),
            ],
            color={ft.ControlState.DEFAULT: row_color, ft.ControlState.HOVERED: AppTheme.SURFACE_LIGHT}
        ))
        self.page.update()

    def on_search_complete(self):
        self.btn_start.disabled = False
        self.btn_start.bgcolor = AppTheme.PRIMARY
        self.btn_stop.disabled = True
        self.btn_stop.bgcolor = Colors.with_opacity(0.3, AppTheme.ERROR)
        self.btn_export.disabled = len(self.data_rows) == 0
        self.btn_export.bgcolor = AppTheme.SUCCESS if len(self.data_rows) > 0 else Colors.with_opacity(0.3, AppTheme.SUCCESS)
        
        self.update_status(self.get_text('status_ready'))
        self.add_log(f"تم استخراج {len(self.data_rows)} شركة" if self.is_arabic else f"Extracted {len(self.data_rows)}", is_success=True)
        self.page.update()

    async def run_search(self):
        try:
            self.add_log("Initializing scraper...")
            self.scraper.on_status_update = lambda msg: self.update_status(msg, is_running=True)
            self.scraper.on_data_found = self.add_data_row
            self.scraper.on_complete = self.on_search_complete
            
            self.add_log("Starting search...")
            await self.scraper.search(
                self.txt_business.value, 
                self.txt_region.value, 
                self.txt_city.value, 
                self.txt_district.value or ""
            )
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}"
            self.add_log(error_msg, is_error=True)
            self.add_log(f"Details: {traceback.format_exc()[:200]}", is_error=True)
            print(f"SEARCH ERROR: {traceback.format_exc()}")  # Print to console
            self.on_search_complete()

    def start_search(self, e):
        if not self.txt_business.value or not self.txt_region.value or not self.txt_city.value:
            self.add_log(self.get_text('validation_error'), is_error=True)
            if not self.txt_business.value: self.txt_business.border_color = AppTheme.ERROR
            if not self.txt_region.value: self.txt_region.border_color = AppTheme.ERROR
            if not self.txt_city.value: self.txt_city.border_color = AppTheme.ERROR
            self.page.update()
            return
        
        self.txt_business.border_color = AppTheme.BORDER
        self.txt_region.border_color = AppTheme.BORDER
        self.txt_city.border_color = AppTheme.BORDER
        
        district_text = f" - {self.txt_district.value}" if self.txt_district.value else ""
        search_info = f"{self.txt_business.value} | {self.txt_city.value}{district_text}"
        
        self.add_log(f"{self.get_text('search_query')} {search_info}")
        self.update_status(self.get_text('status_running'), is_running=True)
        
        self.data_rows.clear()
        self.data_table.rows.clear()
        self.log_view.controls.clear()
        self.stats = {'total': 0, 'phones': 0, 'emails': 0, 'websites': 0}
        self.update_stats()
        self.search_start_time = datetime.now()
        
        self.btn_start.disabled = True
        self.btn_start.bgcolor = Colors.with_opacity(0.3, AppTheme.PRIMARY)
        self.btn_stop.disabled = False
        self.btn_stop.bgcolor = AppTheme.ERROR
        self.btn_export.disabled = True
        self.btn_export.bgcolor = Colors.with_opacity(0.3, AppTheme.SUCCESS)
        self.page.update()
        
        # Use page.run_task for proper Flet async execution
        self.page.run_task(self.run_search)

    def stop_search(self, e):
        self.scraper.stop()
        self.add_log(self.get_text('status_stopped'), is_error=True)
        self.update_status(self.get_text('status_stopped'))
        self.on_search_complete()

    def clear_data(self, e):
        self.data_rows.clear()
        self.data_table.rows.clear()
        self.stats = {'total': 0, 'phones': 0, 'emails': 0, 'websites': 0}
        self.update_stats()
        self.btn_export.disabled = True
        self.btn_export.bgcolor = Colors.with_opacity(0.3, AppTheme.SUCCESS)
        self.add_log("تم مسح البيانات" if self.is_arabic else "Data cleared")
        self.page.update()

    def export_data(self, e):
        if not self.data_rows:
            self.add_log("لا توجد بيانات" if self.is_arabic else "No data", is_error=True)
            return
        try:
            output_dir = Path(OUTPUT_DIR)
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_leads_{timestamp}.xlsx"
            filepath = output_dir / filename
            
            df = pd.DataFrame(self.data_rows)
            columns_map = {'name': 'Business Name', 'phone': 'Phone', 'address': 'Address', 'website': 'Website', 'emails': 'Email', 'socials': 'Social Media', 'latitude': 'Lat', 'longitude': 'Lng', 'url': 'Maps URL'}
            existing_cols = [c for c in columns_map.keys() if c in df.columns]
            df = df[existing_cols]
            df.rename(columns=columns_map, inplace=True)
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            self.add_log(f"تم التصدير: {filename}" if self.is_arabic else f"Exported: {filename}", is_success=True)
            import subprocess
            subprocess.Popen(f'explorer /select,"{filepath.absolute()}"')
        except Exception as ex:
            self.add_log(f"Export Error: {str(ex)}", is_error=True)

def main(page: ft.Page):
    app = ScraperApp(page)

if __name__ == "__main__":
    ft.app(target=main)
