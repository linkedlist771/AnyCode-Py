from __future__ import annotations

import flet as ft

from anycode_py.ui.components import theming
from anycode_py.ui.controllers.chat_controller import ChatController
from anycode_py.ui.models.chat import ChatModel


class HeaderBar:
    """Top header bar with model selector and quick actions."""

    def __init__(self, controller: ChatController, model: ChatModel) -> None:
        self.controller = controller
        self.model = model
        self.selected_model_ref = ft.Ref[ft.Text]()
        self.dropdown_ref = ft.Ref[ft.Container]()

    def build(self) -> ft.Container:
        dropdown_items = ft.Column(
            [
                ft.Container(
                    content=ft.Text(model_name, size=14, color=theming.TEXT_PRIMARY),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    on_click=self._select_model(model_name),
                    on_hover=lambda e: (
                        setattr(e.control, "bgcolor", theming.SIDEBAR_HOVER_BG if e.data == "true" else None)
                        or e.control.update()
                    ),
                )
                for model_name in self.model.available_models
            ],
            spacing=0,
        )

        dropdown_container = ft.Container(
            ref=self.dropdown_ref,
            content=dropdown_items,
            bgcolor=theming.MAIN_BG,
            border=ft.border.all(1, theming.BORDER_COLOR),
            border_radius=8,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            width=200,
        )

        def toggle_dropdown(e):
            dropdown_container.visible = not dropdown_container.visible
            self.controller.update_page()

        model_selector = ft.Stack(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                self.model.selected_model,
                                size=16,
                                color=theming.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_500,
                                ref=self.selected_model_ref,
                            ),
                            ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=theming.TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                    on_click=toggle_dropdown,
                ),
                ft.Container(content=dropdown_container, top=35, left=0),
            ]
        )

        return ft.Container(
            content=ft.Row(
                [
                    model_selector,
                    ft.Container(expand=True),
                    ft.IconButton(ft.Icons.FILE_UPLOAD_OUTLINED, icon_size=20, icon_color=theming.TEXT_SECONDARY),
                    ft.IconButton(ft.Icons.MORE_HORIZ, icon_size=20, icon_color=theming.TEXT_SECONDARY),
                ]
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            border=ft.border.only(bottom=ft.BorderSide(1, theming.BORDER_COLOR)),
        )

    def _select_model(self, model_name: str):
        def handler(e):
            self.controller.select_model(model_name)
            if self.dropdown_ref.current:
                self.dropdown_ref.current.visible = False
            self.update_label(model_name)
            self.controller.update_page()

        return handler

    def update_label(self, model_name: str) -> None:
        if self.selected_model_ref.current:
            self.selected_model_ref.current.value = model_name
