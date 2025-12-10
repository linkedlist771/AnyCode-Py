from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import flet as ft

from anycode_py.ui.models.chat import ChatModel, Conversation, Message

from anycode_py.process_manager.codex import CodexProcessManager

if TYPE_CHECKING:
    from anycode_py.ui.views.main_view import ChatView


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

    def select_conversation(self, session_id: str) -> None:
        self.model.select_conversation(session_id)
        if self.view:
            self.view.refresh_sidebar()
            self.view.refresh_messages(self.model.active_conversation)
        self.page.update()

    def load_more_conversations(self) -> None:
        """Fetch another page of conversations and refresh the sidebar."""
        added = self.model.load_more_conversations()
        if added and self.view:
            self.view.refresh_sidebar()
            self.page.update()

    async def send_message(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return

        message = self.model.add_message("user", text)
        if self.view:
            self.view.append_user_message(message)

        process_manager: CodexProcessManager | None = None
        session_id = self.model.active_conversation.id if self.model.active_conversation else None

        try:
            process_manager = await CodexProcessManager.create()
            if session_id:
                await process_manager.resume(session_id=session_id)
            async for line in process_manager.chat(text):
                self.add_assistant_reply(str(line))
        except Exception as exc:
            self.add_assistant_reply(f"Error: {exc}")
        finally:
            if process_manager:
                await process_manager.close()

        # self.show_snackbar(f"Message sent: {text[:50]}...")
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
