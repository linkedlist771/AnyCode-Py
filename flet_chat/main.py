import flet as ft
from dotenv import load_dotenv
from .app import ChatApp

load_dotenv()


async def main(page: ft.Page):
    page.title = "Codex Chat"
    page.bgcolor = "#ffffff"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed="#10a37f",
        font_family="Inter, Segoe UI, Roboto, sans-serif",
    )

    page.window.width = 1000
    page.window.height = 800
    page.window.min_width = 500
    page.window.min_height = 600

    app = ChatApp(page)
    page.add(app)

    # 初始化
    await app.initialize_codex()


if __name__ == "__main__":
    ft.app(target=main)
