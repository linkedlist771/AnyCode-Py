from __future__ import annotations

import asyncio

import flet as ft
import pyperclip

from anycode_py.ui.components import theming
from anycode_py.ui.controllers.chat_controller import ChatController
from anycode_py.ui.models.chat import Message


class CodeBlock:
    """Reusable code block with copy support."""

    def __init__(self, code_text: str, language: str = "python") -> None:
        self.code_text = code_text
        self.language = language

    def build(self) -> ft.Container:
        async def copy_code(e):
            try:
                pyperclip.copy(self.code_text)
                e.control.content.controls[1].value = "Copied!"
                e.control.update()
                await asyncio.sleep(1)
                e.control.content.controls[1].value = "Copy"
                e.control.update()
            except Exception:
                pass

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(self.language, size=12, color=theming.TEXT_SECONDARY),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.CONTENT_COPY, size=14, color=theming.TEXT_SECONDARY),
                                            ft.Text("Copy", size=12, color=theming.TEXT_SECONDARY),
                                        ],
                                        spacing=4,
                                    ),
                                    on_click=copy_code,
                                    on_hover=lambda e: (
                                        setattr(
                                            e.control,
                                            "bgcolor",
                                            theming.SIDEBAR_HOVER_BG if e.data == "true" else None,
                                        )
                                        or e.control.update()
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=4,
                                ),
                            ]
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border=ft.border.only(bottom=ft.BorderSide(1, theming.BORDER_COLOR)),
                    ),
                    ft.Container(
                        content=ft.Text(
                            self.code_text,
                            size=13,
                            font_family="monospace",
                            color=theming.TEXT_PRIMARY,
                            selectable=True,
                        ),
                        padding=ft.padding.all(12),
                    ),
                ],
                spacing=0,
            ),
            bgcolor=theming.CODE_BG,
            border_radius=8,
            border=ft.border.all(1, theming.BORDER_COLOR),
        )


class UserMessageBubble:
    """User message bubble with edit & copy actions."""

    def __init__(self, message: Message, controller: ChatController):
        self.message = message
        self.controller = controller

    def build(self) -> ft.Container:
        message_textfield = ft.Ref[ft.TextField]()
        message_display = ft.Ref[ft.Text]()
        edit_mode = ft.Ref[ft.Container]()
        view_mode = ft.Ref[ft.Container]()

        async def copy_message(e):
            try:
                pyperclip.copy(self.message.content)
                e.control.icon = ft.Icons.CHECK
                self.controller.update_page()
                await asyncio.sleep(1)
                e.control.icon = ft.Icons.CONTENT_COPY_OUTLINED
                self.controller.update_page()
            except Exception:
                pass

        def edit_message(e):
            view_mode.current.visible = False
            edit_mode.current.visible = True
            message_textfield.current.value = self.message.content
            self.controller.update_page()

        def save_edit(e):
            self.message.content = message_textfield.current.value
            view_mode.current.visible = True
            edit_mode.current.visible = False
            message_display.current.value = self.message.content
            self.controller.update_page()

        def cancel_edit(e):
            view_mode.current.visible = True
            edit_mode.current.visible = False
            self.controller.update_page()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        ref=view_mode,
                        content=ft.Row(
                            [
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                self.message.content,
                                                size=14,
                                                color=theming.TEXT_PRIMARY,
                                                selectable=True,
                                                ref=message_display,
                                            ),
                                        ]
                                    ),
                                    bgcolor=theming.USER_BUBBLE_BG,
                                    border_radius=16,
                                    padding=ft.padding.all(16),
                                    width=600,
                                ),
                            ]
                        ),
                    ),
                    ft.Container(
                        ref=edit_mode,
                        visible=False,
                        content=ft.Row(
                            [
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.TextField(
                                                ref=message_textfield,
                                                multiline=True,
                                                min_lines=5,
                                                max_lines=10,
                                                border_color=theming.BORDER_COLOR,
                                                text_size=14,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Container(expand=True),
                                                    ft.TextButton("Cancel", on_click=cancel_edit),
                                                    ft.ElevatedButton("Save", on_click=save_edit),
                                                ],
                                                spacing=8,
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    bgcolor=theming.USER_BUBBLE_BG,
                                    border_radius=16,
                                    padding=ft.padding.all(16),
                                    width=600,
                                ),
                            ]
                        ),
                    ),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.Icons.EDIT_OUTLINED,
                                icon_size=16,
                                icon_color=theming.TEXT_SECONDARY,
                                on_click=edit_message,
                                tooltip="Edit message",
                            ),
                            ft.IconButton(
                                ft.Icons.CONTENT_COPY_OUTLINED,
                                icon_size=16,
                                icon_color=theming.TEXT_SECONDARY,
                                on_click=copy_message,
                                tooltip="Copy message",
                            ),
                        ]
                    ),
                ],
                spacing=4,
            ),
            padding=ft.padding.only(left=60, right=20, top=20, bottom=10),
        )


class AssistantMessageBlock:
    """Assistant response block with optional code and thought dialog."""

    def __init__(self, message: Message, controller: ChatController):
        self.message = message
        self.controller = controller

    def build(self) -> ft.Container:
        thought_expanded = ft.Ref[ft.Column]()
        thought_icon = ft.Ref[ft.Icon]()

        async def copy_message(e):
            try:
                pyperclip.copy(self.message.content)
                e.control.icon = ft.Icons.CHECK
                self.controller.update_page()
                await asyncio.sleep(1)
                e.control.icon = ft.Icons.CONTENT_COPY_OUTLINED
                self.controller.update_page()
            except Exception:
                pass

        def toggle_thought(e):
            if thought_expanded.current.visible:
                thought_expanded.current.visible = False
                thought_icon.current.name = ft.Icons.CHEVRON_RIGHT
            else:
                self._show_thought_dialog()
            self.controller.update_page()

        controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text("Thought for 47s", size=13, color=theming.TEXT_SECONDARY),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=theming.TEXT_SECONDARY, ref=thought_icon),
                    ],
                    spacing=4,
                ),
                on_click=toggle_thought,
                ink=True,
            ),
            ft.Column(
                [
                    ft.Container(height=8),
                    ft.Text("Detailed thinking process...", size=12, color=theming.TEXT_SECONDARY, italic=True),
                ],
                ref=thought_expanded,
                visible=False,
            ),
            ft.Container(height=8),
            ft.Row(
                [
                    ft.Text("🔵", size=14),
                    ft.Text("🟡", size=14),
                    ft.Text("🔴", size=14),
                    ft.Text("🟠", size=14),
                    ft.Container(width=4),
                    ft.Text("Sources", size=13, color=theming.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                ],
                spacing=2,
            ),
            ft.Container(height=16),
            ft.Markdown(
                value=self.message.content,
                selectable=True,
                code_theme="atom-one-dark",
                on_tap_link=lambda e: self.controller.show_snackbar(f"Open link: {e.data}"),
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            ),
            # ft.Container(height=16),
            # ft.Text(
            #     "1. Text 到底能不能交互 / 复制?",
            #     size=16,
            #     color=theming.TEXT_PRIMARY,
            #     weight=ft.FontWeight.W_600,
            #     selectable=True,
            # ),
            # ft.Container(height=12),
            # ft.Text(
            #     "默认行为",
            #     size=14,
            #     color=theming.TEXT_PRIMARY,
            #     weight=ft.FontWeight.W_600,
            #     selectable=True,
            # ),
            # ft.Container(height=8),
            # ft.Row(
            #     [
            #         ft.Text("•", size=14, color=theming.TEXT_PRIMARY),
            #         ft.Container(width=8),
            #         ft.Column(
            #             [
            #                 ft.Text(
            #                     "Flet 里的大部分控件默认都是不可选中的，包括 Text。",
            #                     size=14,
            #                     color=theming.TEXT_PRIMARY,
            #                     selectable=True,
            #                 ),
            #                 ft.Row(
            #                     [
            #                         ft.Text(
            #                             '所以你现在看到 "文字不能选、不能复制"，大概率是因为用的是默认配置。',
            #                             size=14,
            #                             color=theming.TEXT_PRIMARY,
            #                             selectable=True,
            #                         ),
            #                         ft.Container(
            #                             content=ft.Text("flet.dev +1", size=11, color=theming.TEXT_SECONDARY),
            #                             bgcolor="#f0f0f0",
            #                             border_radius=4,
            #                             padding=ft.padding.symmetric(horizontal=6, vertical=2),
            #                         ),
            #                     ],
            #                     spacing=8,
            #                     wrap=True,
            #                 ),
            #             ],
            #             spacing=4,
            #             expand=True,
            #         ),
            #     ],
            #     alignment=ft.MainAxisAlignment.START,
            #     vertical_alignment=ft.CrossAxisAlignment.START,
            # ),
            # ft.Container(height=16),
            # ft.Text(
            #     "让 Text 可选 & 可复制",
            #     size=14,
            #     color=theming.TEXT_PRIMARY,
            #     weight=ft.FontWeight.W_600,
            #     selectable=True,
            # ),
            # ft.Container(height=8),
            # ft.Row(
            #     [
            #         ft.Text("1.", size=14, color=theming.TEXT_PRIMARY),
            #         ft.Container(width=8),
            #         ft.Text(
            #             "直接把 Text 变成可选：",
            #             size=14,
            #             color=theming.TEXT_PRIMARY,
            #             selectable=True,
            #         ),
            #     ]
            # ),
            # ft.Container(height=12),
        ]

        if self.message.code:
            controls.append(CodeBlock(self.message.code, self.message.language or "python").build())
            controls.append(ft.Container(height=8))

        controls.append(
            ft.Row(
                [
                    ft.IconButton(
                        ft.Icons.CONTENT_COPY_OUTLINED,
                        icon_size=16,
                        icon_color=theming.TEXT_SECONDARY,
                        tooltip="Copy message",
                        on_click=copy_message,
                    ),
                    # ft.Container(width=8),
                    # ft.Container(
                    #     content=ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=20, color=theming.TEXT_SECONDARY),
                    #     width=32,
                    #     height=32,
                    #     bgcolor=theming.MAIN_BG,
                    #     border_radius=16,
                    #     border=ft.border.all(1, theming.BORDER_COLOR),
                    #     alignment=ft.alignment.center,
                    # ),
                    # ft.Container(expand=True),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )

        return ft.Container(
            content=ft.Column(controls, spacing=0),
            padding=ft.padding.only(left=20, right=60, top=10, bottom=20),
        )

    def _show_thought_dialog(self) -> None:
        page = self.controller.page
        dlg = ft.AlertDialog(
            title=ft.Text("Thought Process (47s)", size=18, weight=ft.FontWeight.W_600),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Analysis Steps:", size=14, weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Text("1. 理解用户关于 TextButton 和滚动的问题", size=13),
                        ft.Container(height=4),
                        ft.Text("2. 查阅 Flet 文档的文本选择能力", size=13),
                        ft.Container(height=4),
                        ft.Text("3. 关注 Text 控件的 selectable 参数", size=13),
                        ft.Container(height=4),
                        ft.Text("4. 准备示例代码与解释", size=13),
                        ft.Container(height=4),
                        ft.Text("5. 组织清晰的回答结构", size=13),
                        ft.Container(height=16),
                        ft.Text("Sources Consulted:", size=14, weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Text("🔵 Flet official documentation", size=13),
                        ft.Text("🟡 Python API reference", size=13),
                        ft.Text("🔴 Community examples", size=13),
                        ft.Text("🟠 GitHub issues and discussions", size=13),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=400,
                width=500,
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: page.close(dlg))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg)
