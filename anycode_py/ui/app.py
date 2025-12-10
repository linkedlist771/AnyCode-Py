from __future__ import annotations

import flet as ft

from anycode_py.ui.components import theming
from anycode_py.ui.controllers.chat_controller import ChatController
from anycode_py.ui.models.chat import ChatModel
from anycode_py.ui.views.main_view import ChatView


async def main(page: ft.Page) -> None:
    """Entry point for the Chat UI using MVC."""
    page.title = "AnyCode-Py"
    page.bgcolor = theming.MAIN_BG
    page.padding = 0
    page.spacing = 0

    page.window.width = 1408
    page.window.height = 900
    page.window.min_width = 800
    page.window.min_height = 600
    page.window.center()

    model = ChatModel()
    controller = ChatController(page, model)
    chat_view = ChatView(page, controller, model)
    chat_view.mount()


if __name__ == "__main__":
    ft.app(target=main)
