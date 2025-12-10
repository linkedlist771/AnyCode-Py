from __future__ import annotations

import flet as ft

from anycode_py.ui.components import theming
from anycode_py.ui.controllers.chat_controller import ChatController
from anycode_py.ui.models.chat import Conversation, ChatModel


class Sidebar:
    """Sidebar view responsible for navigation and conversation list."""

    def __init__(self, controller: ChatController, model: ChatModel) -> None:
        self.controller = controller
        self.model = model

    def build(self) -> ft.Container:
        conversation_list = ft.Column(
            [self._conversation_item(conv) for conv in self.model.conversations],
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Container(
            content=ft.Column(
                [
                    self._top_icons(),
                    self._search_box(),
                    self._nav_section(),
                    ft.Container(height=8),
                    self._new_project_button(),
                    self._projects_list(),
                    ft.Divider(height=1, color=theming.BORDER_COLOR),
                    ft.Container(
                        content=conversation_list,
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=4),
                    ),
                    self._user_avatar(),
                ],
                spacing=0,
                expand=True,
            ),
            width=260,
            bgcolor=theming.SIDEBAR_BG,
            border=ft.border.only(right=ft.BorderSide(1, theming.BORDER_COLOR)),
        )

    # --- Sections ------------------------------------------------------- #
    def _top_icons(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.GRID_VIEW_ROUNDED, icon_size=20, icon_color=theming.TEXT_SECONDARY),
                    ft.IconButton(ft.Icons.EDIT_SQUARE, icon_size=20, icon_color=theming.TEXT_SECONDARY),
                ],
                spacing=0,
            ),
            padding=ft.padding.only(left=8, right=4, top=4),
        )

    def _search_box(self) -> ft.Container:
        return ft.Container(
            content=ft.TextField(
                hint_text="Search",
                prefix_icon=ft.Icons.SEARCH,
                border_radius=8,
                border_color=theming.BORDER_COLOR,
                focused_border_color=theming.TEXT_SECONDARY,
                content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
                text_size=14,
                hint_style=ft.TextStyle(color=theming.TEXT_SECONDARY, size=14),
            ),
            padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
        )

    def _nav_section(self) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    self._nav_item(ft.Icons.AUTO_AWESOME, "ChatGPT"),
                    self._nav_item(ft.Icons.APPS, "GPTs", has_arrow=True),
                ],
                spacing=2,
            ),
            padding=ft.padding.symmetric(horizontal=4),
        )

    def _new_project_button(self) -> ft.Container:
        return ft.Container(
            content=ft.Column([self._nav_item(ft.Icons.ADD, "New project")], spacing=2),
            padding=ft.padding.symmetric(horizontal=4),
        )

    def _projects_list(self) -> ft.Container:
        projects = ["y", "ZemengFeng", "lumina", "See more"]
        icons = [ft.Icons.FOLDER_OUTLINED, ft.Icons.FOLDER_OUTLINED, ft.Icons.FOLDER_OUTLINED, ft.Icons.MORE_HORIZ]
        return ft.Container(
            content=ft.Column(
                [self._project_item(icon, name) for icon, name in zip(icons, projects)],
                spacing=2,
            ),
            padding=ft.padding.symmetric(horizontal=4),
        )

    def _user_avatar(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Text("bf", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                        width=32,
                        height=32,
                        bgcolor="#8b5cf6",
                        border_radius=16,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(width=10),
                    ft.Text("bf", size=14, color=theming.TEXT_PRIMARY, weight=ft.FontWeight.W_500),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(12),
            border=ft.border.only(top=ft.BorderSide(1, theming.BORDER_COLOR)),
        )

    # --- Items ---------------------------------------------------------- #
    def _nav_item(self, icon, text: str, has_arrow: bool = False, on_click=None) -> ft.Container:
        row_content = [
            ft.Icon(icon, size=18, color=theming.TEXT_PRIMARY),
            ft.Container(width=10),
            ft.Text(text, size=14, color=theming.TEXT_PRIMARY, weight=ft.FontWeight.W_400),
        ]
        if has_arrow:
            row_content.append(ft.Container(expand=True))
            row_content.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=theming.TEXT_SECONDARY))

        return ft.Container(
            content=ft.Row(row_content, spacing=0),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=8,
            on_click=on_click,
            on_hover=lambda e: (
                setattr(e.control, "bgcolor", theming.SIDEBAR_HOVER_BG if e.data == "true" else None)
                or e.control.update()
            ),
        )

    def _project_item(self, icon, text: str, on_click=None) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color=theming.TEXT_SECONDARY),
                    ft.Container(width=10),
                    ft.Text(text, size=14, color=theming.TEXT_PRIMARY),
                ],
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=8,
            on_click=on_click,
            on_hover=lambda e: (
                setattr(e.control, "bgcolor", theming.SIDEBAR_HOVER_BG if e.data == "true" else None)
                or e.control.update()
            ),
        )

    def _conversation_item(self, conversation: Conversation) -> ft.Container:
        row_content = [
            ft.Text(
                conversation.title,
                size=14,
                color=theming.TEXT_PRIMARY,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
                expand=True,
            ),
        ]
        if conversation.indicator:
            row_content.append(
                ft.Container(
                    width=8,
                    height=8,
                    bgcolor=theming.ACCENT_BLUE,
                    border_radius=4,
                )
            )

        def click_handler(e):
            self.controller.select_conversation(conversation.title)

        return ft.Container(
            content=ft.Row(row_content, spacing=8),
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=8,
            bgcolor=theming.SELECTED_BG if conversation.selected else None,
            border=ft.border.only(left=ft.BorderSide(3, theming.ACCENT_BLUE)) if conversation.selected else None,
            on_click=click_handler,
            on_hover=lambda e: (
                setattr(
                    e.control,
                    "bgcolor",
                    theming.SIDEBAR_HOVER_BG
                    if e.data == "true" and not conversation.selected
                    else (theming.SELECTED_BG if conversation.selected else None),
                )
                or e.control.update()
            )
            if not conversation.selected
            else None,
        )
