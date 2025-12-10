import flet as ft


class CallistoColors:
    # Main Backgrounds
    BG_MAIN = "#FFFFFF"  # Main chat area
    BG_SIDEBAR = "#F9F9F9"  # Sidebar background

    # Text
    TEXT_PRIMARY = "#0D0D0D"
    TEXT_SECONDARY = "#666666"
    TEXT_TERTIARY = "#8E8E8E"

    # Message Bubbles
    BUBBLE_USER_BG = "#F4F4F4"
    BUBBLE_USER_TEXT = "#0D0D0D"

    # Accents
    ACCENT = "#10A37F"  # OpenAI Green-ish
    ICON_DEFAULT = "#1C1C1C"

    # Borders
    BORDER_LIGHT = "#E5E5E5"


class TextStyles:
    MSG_USER = ft.TextStyle(size=15, color=CallistoColors.TEXT_PRIMARY, weight=ft.FontWeight.W_400)
    MSG_ASSISTANT = ft.TextStyle(size=15, color=CallistoColors.TEXT_PRIMARY, weight=ft.FontWeight.W_400)
    SIDEBAR_ITEM = ft.TextStyle(size=14, color=CallistoColors.TEXT_PRIMARY)
    HEADER_TITLE = ft.TextStyle(size=16, weight=ft.FontWeight.W_600, color=CallistoColors.TEXT_SECONDARY)
