import json
from datetime import datetime
from typing import Any, Dict, Optional
from loguru import logger
import flet as ft

from .base import CodexWidget
from .message_bubbles import AssistantMessageWidget, SystemInfoWidget
from .action_widgets import ReasoningWidget, CommandWidget
from .advanced_widgets import EditWidget, TodoListWidget


class CodexWidgetFactory:
    """
    工厂模式：根据 Codex 事件类型创建对应的 UI 组件
    支持完整 Codex IPC 协议
    """

    @staticmethod
    def create_widget(chunk: Dict[str, Any]) -> Optional[CodexWidget]:
        event_type = chunk.get("type")

        # --- 1. Top-Level Events ---

        # Thread / Turn Events
        if event_type == "thread.started":
            # Display "Codex session started" (System Message)
            # return SystemInfoWidget(f"sys_thread_{datetime.now().timestamp()}", "thread.started")
            return None  # User requested not to show "Session Started" in previous refinement, or show minimal

        elif event_type == "turn.started":
            return None  # Skip as per spec

        elif event_type == "turn.completed":
            # Display Token Usage
            return SystemInfoWidget(f"sys_turn_{datetime.now().timestamp()}", "turn.completed")

        elif event_type == "turn.failed" or event_type == "error":
            return SystemInfoWidget(f"sys_error_{datetime.now().timestamp()}", "error")

        elif event_type == "session_meta":
            # "Codex session started (ID: ...)"
            # return SystemInfoWidget(f"sys_meta_{datetime.now().timestamp()}", "thread.started")
            return None

        # --- 2. Item Events (item.started, item.updated, item.completed) ---
        elif event_type in ["item.started", "item.updated", "item.completed"]:
            item = chunk.get("item", {})
            item_id = item.get("id")
            item_type = item.get("type")

            if not item_id:
                return None

            if item_type == "reasoning":
                return ReasoningWidget(item_id)

            elif item_type == "command_execution":
                return CommandWidget(item_id)

            elif item_type == "agent_message":
                return AssistantMessageWidget(item_id)

            elif item_type == "file_change":
                return EditWidget(item_id)

            elif item_type == "mcp_tool_call":
                # TODO: MCP Widget
                return None

            elif item_type == "web_search":
                # TODO: WebSearch Widget
                return None

            elif item_type == "todo_list":
                return TodoListWidget(item_id)

            # Fallback
            logger.warning(f"Unknown item type: {item_type}, raw: {json.dumps(item)}")
            # Render as assistant bubble so user can see raw text if present
            return AssistantMessageWidget(item_id)

        # --- 3. Response Item (response_item) ---
        elif event_type == "response_item":
            # payload: { type: ..., ... } or { role: ..., content: ... }
            payload = chunk.get("payload", {})

            # 3.1 Role-based (User/Assistant Messages)
            if "role" in payload:
                role = payload.get("role")

                # ID generation is tricky for response_item as it might not be streaming per se with an ID
                # But usually response_item updates are single-shot or handled by `item.*` for streaming agent_message.
                # If we receive response_item, it might be a finalized message.

                item_id = f"resp_{datetime.now().timestamp()}"

                if role == "assistant":
                    return AssistantMessageWidget(item_id)
                elif role == "user":
                    # User bubble is usually added manually on submit, so skip here?
                    # Or render if it's history replayed.
                    return None

            # 3.2 Specific Payload Types
            p_type = payload.get("type")
            if p_type == "reasoning":
                # Handle reasoning payload
                # summary = payload.get("summary") ...
                return None  # Usually handled via item.reasoning

            elif p_type in ["function_call", "custom_tool_call"]:
                # Handled via item.command_execution usually?
                return None

        return None
