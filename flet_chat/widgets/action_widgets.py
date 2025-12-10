import flet as ft
from typing import Any, Dict
from ..styles import CallistoColors
from .base import CodexWidget


class ReasoningWidget(CodexWidget):
    """
    思考过程 (ChatGPT 'Thought for...' Style)
    Refined: Minimal grey text, click to expand.
    """

    def __init__(self, item_id: str):
        super().__init__(item_id)
        self.padding = ft.padding.only(bottom=10)

        # Header (Clickable to toggle)
        # Style: "Thought for Xs >" in grey, clickable.
        self.header_text = ft.Text("Thinking...", size=13, color="#666666", weight=ft.FontWeight.W_500)
        self.arrow_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, size=16, color="#666666")

        # 使用 Container 的 on_click，这是最稳定的方式
        self.header = ft.Container(
            content=ft.Row([self.header_text, self.arrow_icon], spacing=4),
            padding=ft.padding.symmetric(vertical=4, horizontal=0),
            on_click=self.toggle_details,
            border_radius=4,
            ink=True,
        )

        # Details (Collapsed by default)
        self.details_view = ft.Markdown(
            "",
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            selectable=True,
            md_style_sheet=ft.MarkdownStyleSheet(p_text_style=ft.TextStyle(size=13, color="#444444")),
        )
        self.details_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=4),
                    ft.Divider(height=1, color="#E5E5E5"),
                    ft.Container(height=4),
                    self.details_view,
                ]
            ),
            padding=ft.padding.only(left=8),
            visible=False,
        )

        self.content = ft.Column(controls=[self.header, self.details_container], spacing=0)

    def toggle_details(self, e):
        self.details_container.visible = not self.details_container.visible
        self.arrow_icon.name = (
            ft.Icons.KEYBOARD_ARROW_DOWN if self.details_container.visible else ft.Icons.KEYBOARD_ARROW_RIGHT
        )
        self.safe_update()

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        text = data.get("text", "")
        self.details_view.value = text

        if is_completed:
            # Mock duration
            self.header_text.value = f"Thought for 2s"

        self.safe_update()


class CommandWidget(CodexWidget):
    """
    命令行执行
    """

    def __init__(self, item_id: str):
        super().__init__(item_id)
        self.bgcolor = "transparent"
        self.padding = ft.padding.symmetric(vertical=5)

        self.cmd_text = ft.Text(
            "", font_family="Consolas, monospace", color="#333333", weight=ft.FontWeight.W_500, size=13
        )
        self.output_view = ft.Markdown(
            "",
            code_theme=ft.MarkdownCodeTheme.GITHUB,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            md_style_sheet=ft.MarkdownStyleSheet(
                code_text_style=ft.TextStyle(font_family="Consolas, monospace", size=12)
            ),
        )

        self.status_icon = ft.Icon(ft.Icons.CIRCLE_OUTLINED, size=14, color="#999999")

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.status_icon,
                            ft.Text("Run:", size=13, color="#666666"),
                            ft.Container(content=self.cmd_text, expand=True),
                        ],
                        spacing=8,
                    ),
                    ft.Container(
                        content=self.output_view,
                        padding=ft.padding.only(left=22),
                        visible=False,  # Hide output initially for cleaner look? Or show? Let's show empty if no output.
                    ),
                ]
            ),
            padding=10,
            border=ft.border.all(1, "#E5E5E5"),
            border_radius=8,
            bgcolor="#FAFAFA",
        )

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        if "command" in data:
            self.cmd_text.value = data["command"]

        output = data.get("aggregated_output", "")
        if output:
            self.output_view.value = f"```bash\n{output}\n```"
            self.content.content.controls[1].visible = True

        if is_completed:
            exit_code = data.get("exit_code")
            status = data.get("status")
            if status == "failed" or (exit_code is not None and exit_code != 0):
                self.status_icon.name = ft.Icons.ERROR_OUTLINE
                self.status_icon.color = ft.Colors.RED_400
            else:
                self.status_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
                self.status_icon.color = "#10A37F"

        self.safe_update()
