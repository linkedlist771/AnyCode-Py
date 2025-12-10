import flet as ft
from typing import Any, Dict
from ..styles import CallistoColors
from .base import CodexWidget


class EditWidget(CodexWidget):
    """
    File Edit / Change visualization
    """

    def __init__(self, item_id: str):
        super().__init__(item_id)
        self.bgcolor = "#FAFAFA"
        self.border = ft.border.all(1, CallistoColors.BORDER_LIGHT)
        self.border_radius = 8
        self.padding = 10

        self.icon = ft.Icon(ft.Icons.EDIT_DOCUMENT, size=16, color=CallistoColors.TEXT_SECONDARY)
        self.title = ft.Text("Editing file...", size=14, weight=ft.FontWeight.W_500, color=CallistoColors.TEXT_PRIMARY)
        self.diff_view = ft.Markdown(
            "", code_theme=ft.MarkdownCodeTheme.GITHUB, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
        )

        self.content = ft.Column([ft.Row([self.icon, self.title], spacing=8), ft.Container(height=4), self.diff_view])

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        file_path = data.get("file_path", "Unknown File")
        change_type = data.get("change_type", "edit")
        self.title.value = f"{change_type.capitalize()}: {file_path}"

        content = data.get("content") or data.get("diff") or ""
        if content:
            self.diff_view.value = f"```diff\n{content}\n```"

        self.safe_update()


class TodoListWidget(CodexWidget):
    """
    Displays the Plan / Todo List
    """

    def __init__(self, item_id: str):
        super().__init__(item_id)
        self.padding = 10
        self.plan_text = ft.Markdown("")
        self.content = ft.Container(content=self.plan_text, padding=10, bgcolor="#F4F4F4", border_radius=8)

    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        todos = data.get("todos", [])
        lines = ["**Plan:**"]
        for todo in todos:
            status = todo.get("status", "pending")
            icon = "○"
            if status == "completed":
                icon = "✓"
            elif status == "in_progress":
                icon = "⏳"
            elif status == "failed":
                icon = "✗"

            lines.append(f"{icon} {todo.get('description')}")

        self.plan_text.value = "\n".join(lines)
        self.safe_update()
