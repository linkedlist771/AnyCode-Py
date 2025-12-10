import flet as ft
from typing import Any, Dict
from ..styles import CallistoColors, TextStyles
from .base import CodexWidget


class UserMessageBubble(ft.Container):
    """
    用户消息气泡 (ChatGPT Style)
    - 浅灰色圆角背景
    - 右侧对齐
    """

    def __init__(self, content: str):
        super().__init__(
            content=ft.Container(
                content=ft.Markdown(
                    content,
                    selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    code_theme=ft.MarkdownCodeTheme.MONOKAI,
                    md_style_sheet=ft.MarkdownStyleSheet(p_text_style=TextStyles.MSG_USER),
                ),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
                bgcolor=CallistoColors.BUBBLE_USER_BG,
                border_radius=24,
                width=None,  # Auto width
            ),
            alignment=ft.alignment.center_right,
            padding=ft.padding.only(bottom=20),
        )


class AssistantMessageWidget(CodexWidget):
    """
    Assistant 消息 (ChatGPT Style)
    - 左侧对齐
    - 无消息气泡背景
    - 左侧显示图标
    """

    def __init__(self, item_id: str):
        super().__init__(item_id)
        self.padding = ft.padding.only(bottom=20)

        self.text_view = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=ft.MarkdownCodeTheme.MONOKAI_SUBLIME,
            md_style_sheet=ft.MarkdownStyleSheet(p_text_style=TextStyles.MSG_ASSISTANT),
        )

        self.icon_container = ft.Container(
            content=ft.Image(src="/icons/icon.png", width=24, height=24, border_radius=12)
            if False
            # TODO: Replace with actual asset if available, else use Icon
            else ft.Container(
                content=ft.Icon(ft.Icons.AUTO_AWESOME, size=16, color="white"),
                width=24,
                height=24,
                bgcolor="#10a37f",
                border_radius=12,
                alignment=ft.alignment.center,
            ),
            alignment=ft.alignment.top_left,
            margin=ft.margin.only(right=16, top=8),  # Align with text top
        )

        self.content = ft.Row(
            controls=[
                self.icon_container,
                ft.Container(content=self.text_view, expand=True, padding=ft.padding.only(top=0)),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
        )

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        text = data.get("text", "")
        self.text_view.value = text
        self.safe_update()


class SystemInfoWidget(CodexWidget):
    """
    系统消息
    """

    def __init__(self, item_id: str, info_type: str):
        super().__init__(item_id)
        self.info_text = ft.Text("", size=12, color=CallistoColors.TEXT_TERTIARY, text_align=ft.TextAlign.CENTER)
        self.content = ft.Container(
            content=self.info_text, alignment=ft.alignment.center, padding=ft.padding.symmetric(vertical=6)
        )
        self.info_type = info_type

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        if self.info_type == "turn.completed":
            usage = data.get("usage", {})
            in_tok = usage.get("input_tokens", 0)
            out_tok = usage.get("output_tokens", 0)
            # 简化显示
            # self.info_text.value = f"Memory Updated ({in_tok}/{out_tok})"
            return  # 暂时不显示 turn completed，稍微干净点

        elif self.info_type == "thread.started":
            self.info_text.value = ""  # 不显示 Session Started

        elif self.info_type == "error" or self.info_type == "turn.failed":
            error_msg = data.get("error", {}).get("message", "Unknown error")
            self.info_text.value = f"Error: {error_msg}"
            self.info_text.color = ft.Colors.RED_400

        if self.info_text.value:
            self.safe_update()
