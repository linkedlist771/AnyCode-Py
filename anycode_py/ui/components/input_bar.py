from __future__ import annotations

import flet as ft

from anycode_py.ui.components import theming
from anycode_py.ui.controllers.chat_controller import ChatController


class InputBar:
    """Bottom input bar with buttons and send action."""

    def __init__(self, controller: ChatController) -> None:
        self.controller = controller
        self.input_field_ref = ft.Ref[ft.TextField]()

    def build(self) -> ft.Container:
        def on_send_click(e):
            if self.input_field_ref.current and self.input_field_ref.current.value:
                text = self.input_field_ref.current.value
                self.input_field_ref.current.value = ""
                self.controller.update_page()
                # Run async chat send without blocking UI thread.
                self.controller.page.run_task(self.controller.send_message, text)

        def on_attach_click(e):
            self.controller.show_snackbar("Attachment feature - select files", bgcolor=theming.ACCENT_BLUE)

        def on_web_click(e):
            self.controller.show_snackbar("Web search enabled", bgcolor=theming.ACCENT_BLUE)

        def on_deep_think_click(e):
            self.controller.show_snackbar("Deep thinking mode activated", bgcolor=theming.ACCENT_BLUE)

        def on_code_click(e):
            self.controller.show_snackbar("Code interpreter enabled", bgcolor=theming.ACCENT_BLUE)

        def on_canvas_click(e):
            self.controller.show_snackbar("Canvas mode - create visual content", bgcolor=theming.ACCENT_BLUE)

        def on_camera_click(e):
            self.controller.show_snackbar("Camera - capture image", bgcolor=theming.ACCENT_BLUE)

        def on_mic_click(e):
            self.controller.show_snackbar("Voice input - speak now", bgcolor=theming.ACCENT_BLUE)

        input_field = ft.TextField(
            ref=self.input_field_ref,
            hint_text="Ask anything",
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
            text_size=14,
            hint_style=ft.TextStyle(color=theming.TEXT_SECONDARY, size=14),
            expand=True,
            multiline=True,
            min_lines=1,
            max_lines=5,
            on_submit=on_send_click,
        )

        return ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(content=input_field, padding=ft.padding.only(left=8, right=8, top=4)),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                ft.Icons.ADD,
                                                icon_size=20,
                                                icon_color=theming.TEXT_SECONDARY,
                                                tooltip="Attach files",
                                                on_click=on_attach_click,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.LANGUAGE,
                                                icon_size=20,
                                                icon_color=theming.TEXT_SECONDARY,
                                                tooltip="Web search",
                                                on_click=on_web_click,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.BOLT,
                                                icon_size=20,
                                                icon_color=theming.TEXT_SECONDARY,
                                                tooltip="Deep think",
                                                on_click=on_deep_think_click,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.CODE,
                                                icon_size=20,
                                                icon_color=theming.TEXT_SECONDARY,
                                                tooltip="Code",
                                                on_click=on_code_click,
                                            ),
                                            ft.IconButton(
                                                ft.Icons.AUTO_FIX_HIGH,
                                                icon_size=20,
                                                icon_color=theming.TEXT_SECONDARY,
                                                tooltip="Canvas",
                                                on_click=on_canvas_click,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    self.controller.model.selected_model.split()[-1],
                                                    size=12,
                                                    color=theming.TEXT_SECONDARY,
                                                ),
                                                bgcolor="#f0f0f0",
                                                border_radius=8,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            ),
                                        ],
                                        spacing=0,
                                    ),
                                    ft.Container(expand=True),
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.Icon(
                                                    ft.Icons.CAMERA_ALT_OUTLINED, size=18, color=theming.TEXT_SECONDARY
                                                ),
                                                width=36,
                                                height=36,
                                                bgcolor="#f0f0f0",
                                                border_radius=18,
                                                alignment=ft.alignment.center,
                                                on_click=on_camera_click,
                                                tooltip="Camera",
                                            ),
                                            ft.Container(
                                                content=ft.Icon(
                                                    ft.Icons.MIC_NONE, size=18, color=theming.TEXT_SECONDARY
                                                ),
                                                width=36,
                                                height=36,
                                                bgcolor="#f0f0f0",
                                                border_radius=18,
                                                alignment=ft.alignment.center,
                                                on_click=on_mic_click,
                                                tooltip="Voice input",
                                            ),
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.ARROW_UPWARD, size=18, color=ft.Colors.WHITE),
                                                width=36,
                                                height=36,
                                                bgcolor="#1a1a1a",
                                                border_radius=18,
                                                alignment=ft.alignment.center,
                                                on_click=on_send_click,
                                                tooltip="Send message",
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(left=4, right=8, bottom=8),
                        ),
                    ],
                    spacing=0,
                ),
                bgcolor="#f9f9f9",
                border_radius=24,
                border=ft.border.all(1, theming.BORDER_COLOR),
            ),
            padding=ft.padding.only(left=20, right=20, bottom=16, top=8),
            bgcolor=theming.MAIN_BG,
        )
