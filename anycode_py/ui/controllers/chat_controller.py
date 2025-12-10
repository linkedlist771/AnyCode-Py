from __future__ import annotations

from typing import Optional

import flet as ft

from anycode_py.ui.models.chat import ChatModel, Conversation, Message


class ChatController:
    """Controller layer that wires user actions to the model and view."""

    def __init__(self, page: ft.Page, model: ChatModel) -> None:
        self.page = page
        self.model = model
        self.view: Optional["ChatView"] = None

    def attach_view(self, view: "ChatView") -> None:
        self.view = view

    # --- Actions --------------------------------------------------------- #
    def select_model(self, model_name: str) -> None:
        self.model.select_model(model_name)
        if self.view:
            self.view.update_model_label(model_name)
        self.page.update()

    def select_conversation(self, title: str) -> None:
        self.model.select_conversation(title)
        if self.view:
            self.view.refresh_messages(self.model.active_conversation)
        self.page.update()

    def send_message(self, text: str) -> None:
        if not text or not text.strip():
            return
        message = self.model.add_message("user", text.strip())
        if self.view:
            self.view.append_user_message(message)
        self.show_snackbar(f"Message sent: {text[:50]}...")
        self.page.update()

    def add_assistant_reply(self, text: str, code: str | None = None, language: str | None = None) -> None:
        message = self.model.add_message(
            "assistant", text, kind="rich" if code else "text", language=language, code=code
        )
        if self.view:
            self.view.append_assistant_message(message)
        self.page.update()

    # --- Helpers --------------------------------------------------------- #
    def show_snackbar(self, message: str, bgcolor: str = "#4caf50") -> None:
        self.page.open(ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor))

    def update_page(self) -> None:
        self.page.update()
