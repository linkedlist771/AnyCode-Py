from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Message:
    """Represents a single chat message."""

    role: str
    content: str
    kind: str = "text"  # text | rich | code
    language: Optional[str] = None
    code: Optional[str] = None


@dataclass
class Conversation:
    """Represents a chat conversation shown in the sidebar."""

    title: str
    selected: bool = False
    indicator: bool = False
    messages: List[Message] = field(default_factory=list)


class ChatModel:
    """In-memory chat state used by the MVC controller."""

    def __init__(self) -> None:
        self.available_models: List[str] = [
            "ChatGPT 5.1",
            "ChatGPT 4o",
            "ChatGPT 4",
            "Claude 3.5 Sonnet",
            "GPT-3.5 Turbo",
        ]
        self.selected_model: str = self.available_models[0]
        self.conversations: List[Conversation] = self._build_conversations()
        self._seed_default_messages()

    def _build_conversations(self) -> List[Conversation]:
        conversations = [
            Conversation("TextButton 和滚动问题", selected=True),
            Conversation("TextButton 用法说明", indicator=True),
            Conversation("代码实现请求"),
            Conversation("UI模型对比"),
            Conversation("2K 分辨率解释"),
            Conversation("罚球排名统计"),
            Conversation("iPhone 中毒风险分析"),
            Conversation("小说生成创新方向"),
            Conversation("小说沙盒创新方向"),
            Conversation("4090bf16 tflops 算力"),
            Conversation("情绪的神经科学解释"),
        ]
        return conversations

    def _seed_default_messages(self) -> None:
        """Populate the selected conversation with the original demo messages."""
        conversation = self.active_conversation
        if not conversation:
            return

        user_message = Message(
            role="user",
            content=(
                "我尝试使用 TextButton，但可能还是需要查看最新的 Flet 文档。"
                "让我等待你那边的反馈，看看正确的实现方式是什么。同时，关于滚动问题，"
                "如果你能提供具体的错误信息或者行为描述，会帮助我更好地定位问题：\n"
                "是否能用鼠标滚轮滚动？\n"
                "是否能拖动滚动条？\n"
                "是否完全无法交互（比如无法选择文字）？\n"
                "这些信息能帮我更准确地找到问题所在 搜索调研下"
            ),
        )

        assistant_text = (
            "先直接把几个关键点说清楚：\n\n"
            "1. Text 到底能不能交互 / 复制?\n"
            "默认行为：Flet 里的大部分控件默认都是不可选中的，包括 Text。\n"
            "让 Text 可选 & 可复制：直接把 Text 变成可选。"
        )
        code_example = 'ft.Text(\n    "Selectable plain text with default style",\n    selectable=True,\n)'

        assistant_message = Message(
            role="assistant",
            content=assistant_text,
            kind="rich",
            code=code_example,
            language="python",
        )

        conversation.messages.extend([user_message, assistant_message])

    @property
    def active_conversation(self) -> Optional[Conversation]:
        for conversation in self.conversations:
            if conversation.selected:
                return conversation
        return self.conversations[0] if self.conversations else None

    def select_model(self, model_name: str) -> None:
        if model_name in self.available_models:
            self.selected_model = model_name

    def select_conversation(self, title: str) -> None:
        for conversation in self.conversations:
            conversation.selected = conversation.title == title

    def add_message(
        self,
        role: str,
        content: str,
        kind: str = "text",
        language: Optional[str] = None,
        code: Optional[str] = None,
    ) -> Message:
        conversation = self.active_conversation
        if conversation is None:
            conversation = Conversation(title="Default", selected=True)
            self.conversations.append(conversation)

        message = Message(role=role, content=content, kind=kind, language=language, code=code)
        conversation.messages.append(message)
        return message
