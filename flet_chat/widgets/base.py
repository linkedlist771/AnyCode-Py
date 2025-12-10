import flet as ft
from typing import Any, Dict
from abc import ABC, abstractmethod


class CodexWidget(ft.Container):
    """
    所有 Codex UI 组件的基类。
    必须实现 update_data 方法以处理流式更新。
    """

    def __init__(self, item_id: str):
        super().__init__(
            padding=0,
            border_radius=8,
            animate_opacity=300,
        )
        self.item_id = item_id

    @abstractmethod
    def update_data(self, data: Dict[str, Any], is_completed: bool = False):
        """处理 item.updated 或 item.completed 数据"""
        pass

    def safe_update(self):
        """安全更新，避免未添加到 page 时报错"""
        try:
            self.update()
        except Exception:
            # 忽略 "Control must be added to the page first"
            pass
