from __future__ import annotations

import flet as ft

from anycode_py.ui.components import theming
from anycode_py.ui.components.header import HeaderBar
from anycode_py.ui.components.input_bar import InputBar
from anycode_py.ui.components.messages import AssistantMessageBlock, UserMessageBubble
from anycode_py.ui.components.sidebar import Sidebar
from anycode_py.ui.controllers.chat_controller import ChatController
from anycode_py.ui.models.chat import ChatModel, Conversation, Message


class ChatView:
    """Main view that composes the sidebar, chat area and input bar."""

    def __init__(self, page: ft.Page, controller: ChatController, model: ChatModel) -> None:
        self.page = page
        self.controller = controller
        self.model = model
        self.header = HeaderBar(controller, model)
        self.sidebar = Sidebar(controller, model)
        self.input_bar = InputBar(controller)
        self.message_column = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
        controller.attach_view(self)

    def build(self) -> ft.Row:
        self.refresh_messages(self.model.active_conversation)

        chat_area = ft.Container(content=self.message_column, expand=True)

        right_side = ft.Container(
            content=ft.Column(
                [
                    self.header.build(),
                    chat_area,
                    self.input_bar.build(),
                ],
                spacing=0,
                expand=True,
            ),
            expand=True,
            bgcolor=theming.MAIN_BG,
        )

        return ft.Row([self.sidebar.build(), right_side], spacing=0, expand=True)

    def mount(self) -> None:
        self.page.add(self.build())

    # --- View update helpers -------------------------------------------- #
    def refresh_messages(self, conversation: Conversation | None) -> None:
        self.message_column.controls.clear()
        if conversation is None:
            return
        for message in conversation.messages:
            if message.role == "user":
                self.append_user_message(message, update=False)
            else:
                self.append_assistant_message(message, update=False)
        self.controller.update_page()

    def append_user_message(self, message: Message, update: bool = True) -> None:
        self.message_column.controls.append(UserMessageBubble(message, self.controller).build())
        if update:
            self.controller.update_page()

    def append_assistant_message(self, message: Message, update: bool = True) -> None:
        self.message_column.controls.append(AssistantMessageBlock(message, self.controller).build())
        if update:
            self.controller.update_page()

    def update_model_label(self, model_name: str) -> None:
        self.header.update_label(model_name)
