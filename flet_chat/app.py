import asyncio
from typing import Optional, Dict
from datetime import datetime
import flet as ft
from loguru import logger
from anycode_py.process_manager.codex import CodexProcessManager
from .widgets.factory import CodexWidgetFactory
from .widgets.base import CodexWidget
from .widgets.message_bubbles import UserMessageBubble
from .styles import CallistoColors, TextStyles


class ChatApp(ft.Row):
    """主聊天应用容器 (Layout: Sidebar | Content)"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.codex: Optional[CodexProcessManager] = None
        self.is_processing = False
        self.active_items: Dict[str, CodexWidget] = {}

        # --- Sidebar Components ---

        # Search Bar
        self.search_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.SEARCH, size=18, color=CallistoColors.TEXT_TERTIARY),
                    ft.Text("Search", size=14, color=CallistoColors.TEXT_TERTIARY),
                ],
                spacing=8,
            ),
            bgcolor="#EFEFEF",  # Slightly darker than sidebar bg
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=6,
            margin=ft.margin.only(bottom=10),
        )

        # Nav Items
        self.nav_items = ft.Column(
            [
                self._create_nav_item(ft.Icons.AUTO_AWESOME, "ChatGPT", active=True),
                self._create_nav_item(ft.Icons.GRID_VIEW, "GPTs"),
                self._create_nav_item(ft.Icons.EDIT_SQUARE, "New project"),
            ],
            spacing=2,
        )

        # Folders / Categories
        self.folders = ft.Column(
            [
                self._create_folder_item("y"),
                self._create_folder_item("ZemengFeng"),
                self._create_folder_item("lumina"),
                self._create_nav_item(ft.Icons.MORE_HORIZ, "See more"),
            ],
            spacing=2,
        )

        # History Sections
        self.history = ft.Column(
            [
                ft.Container(height=20),
                ft.Text("代码实现请求", size=12, color=CallistoColors.TEXT_TERTIARY, weight=ft.FontWeight.W_500),
                self._create_history_item("小说生成创新方向"),
                self._create_history_item("小说沙盒创新方向"),
                self._create_history_item("4090bf16 tflops 算力"),
                self._create_history_item("情绪的神经科学解释"),
            ],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
        )

        # User Profile (Bottom)
        self.user_profile = ft.Container(
            content=ft.Row(
                [
                    ft.CircleAvatar(
                        foreground_image_src="https://avatars.githubusercontent.com/u/123456?v=4",  # Placeholder
                        radius=12,
                        content=ft.Text("bf", size=10),
                    ),
                    ft.Text("bf", size=14, weight=ft.FontWeight.W_500, color=CallistoColors.TEXT_PRIMARY),
                ],
                spacing=10,
            ),
            padding=ft.padding.symmetric(vertical=12, horizontal=8),
            border=ft.border.only(top=ft.BorderSide(1, "#E5E5E5")),
        )

        self.sidebar = ft.Container(
            width=260,
            bgcolor="#F9F9F9",
            padding=ft.padding.all(12),
            content=ft.Column(
                [
                    self.search_bar,
                    self.nav_items,
                    ft.Container(height=10),
                    self.folders,
                    ft.Container(height=10),
                    ft.Container(content=self.history, expand=True),  # Scrollable history
                    self.user_profile,
                ],
                spacing=0,
                expand=True,
            ),
        )

        # --- Main Content Components ---

        # Header "ChatGPT 5.1 Thinking >"
        self.header = ft.Container(
            height=50,
            padding=ft.padding.symmetric(horizontal=20),
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "ChatGPT 5.1 Thinking", size=15, weight=ft.FontWeight.W_600, color="#444444"
                            ),  # Greyish title
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color="#999999"),
                        ],
                        spacing=4,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(ft.Icons.IOS_SHARE, icon_color="#666666", icon_size=18, tooltip="Share"),
                            ft.IconButton(ft.Icons.EDIT_SQUARE, icon_color="#666666", icon_size=18, tooltip="New Chat"),
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # Chat Area
        self.chat_list_view = ft.ListView(
            expand=True,
            spacing=20,
            auto_scroll=True,  # 新消息自动滚动到底部
            padding=ft.padding.only(left=20, right=20, top=20, bottom=120),
        )
        self.chat_container = ft.Container(
            content=self.chat_list_view,
            expand=True,
        )

        # Floating Input Bar
        self.input_field = ft.TextField(
            hint_text="Ask anything",
            border=ft.InputBorder.NONE,
            multiline=True,
            min_lines=1,
            max_lines=5,
            text_size=15,
            content_padding=ft.padding.symmetric(horizontal=0, vertical=10),
            on_submit=self._on_submit_click,
            shift_enter=True,
            # Removed expand=True from TextField directly to prevent vertical expansion issues in some layouts
        )

        # Input Bar Icons
        left_icons = ft.Row(
            [
                ft.Icon(ft.Icons.ADD, color="#666666", size=20),
                ft.Icon(ft.Icons.LANGUAGE, color="#666666", size=18),
                # ft.Icon(ft.Icons.PSYCHOLOGY, color="#666666", size=18), # Generic brain/tool
                ft.Text("5.1 Thinking", size=12, weight=ft.FontWeight.BOLD, color="#666666"),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        right_icons = ft.Row(
            [
                ft.Container(content=ft.Icon(ft.Icons.MIC, color="#666666", size=20), padding=4),
                ft.Container(
                    content=ft.Icon(ft.Icons.GRAPHIC_EQ, color="white", size=16),
                    bgcolor="black",
                    width=32,
                    height=32,
                    border_radius=16,
                    alignment=ft.alignment.center,
                    on_click=self._on_submit_click,  # Make this the "Send" trigger for now
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.input_bar = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            left_icons,
                        ],
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.Container(content=self.input_field, expand=True),  # Wrap in expanding container
                            right_icons,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                spacing=0,
                tight=True,
            ),  # tight=True to prevent Column from expanding vertically
            bgcolor="#F4F4F4",  # Light grey input bg
            border_radius=28,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            width=700,  # Max width
            shadow=None,  # Flat as per screenshots
        )

        self.input_area_container = ft.Container(
            content=self.input_bar,
            alignment=ft.alignment.bottom_center,
            padding=ft.padding.only(bottom=24),
            # 不设置 expand 和高度，让它只占据必要的空间
        )

        # Main Layout
        self.main_content = ft.Container(
            expand=True,
            bgcolor="white",
            content=ft.Column(
                [
                    self.header,
                    ft.Stack(
                        [
                            # 聊天区域 - 可以交互和滚动
                            self.chat_container,
                            # 输入框 - 浮动在底部，不阻挡聊天区域
                            ft.Container(
                                content=self.input_bar,
                                alignment=ft.alignment.bottom_center,
                                padding=ft.padding.only(bottom=24),
                            ),
                        ],
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
        )

        super().__init__(controls=[self.sidebar, self.main_content], expand=True, spacing=0)

    # --- Setup Methods ---

    def _create_nav_item(self, icon, text, active=False):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18, color="#000000" if active else "#555555"),
                    ft.Text(
                        text,
                        size=14,
                        color="#000000" if active else "#333333",
                        weight=ft.FontWeight.W_500 if active else ft.FontWeight.NORMAL,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border_radius=6,
            bgcolor="#EAEAEA" if active else None,
            ink=True,
            on_click=lambda e: print(f"Nav {text}"),
        )

    def _create_folder_item(self, text):
        return ft.Container(
            content=ft.Row(
                [ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color="#555555"), ft.Text(text, size=14, color="#333333")],
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border_radius=6,
            ink=True,
            on_click=lambda e: print(f"Folder {text}"),
        )

    def _create_history_item(self, text):
        return ft.Container(
            content=ft.Text(text, size=13, color="#333333", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border_radius=6,
            ink=True,
            on_click=lambda e: print(f"History {text}"),
        )

    # --- Event Handlers & Core Logic ---

    def _on_submit_click(self, e):
        self.page.run_task(self.handle_submit, e)

    def _on_new_conversation_click(self, e):
        # Reset UI
        self.chat_list_view.controls.clear()
        self.page.update()
        if self.codex:
            self.page.run_task(self.new_conversation, e)

    async def initialize_codex(self):
        if not self.codex:
            try:
                self.codex = await CodexProcessManager.create()
                logger.info("Codex initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Codex: {e}")
                self.chat_list_view.controls.append(ft.Text(f"Error: {e}", color="red"))
                self.page.update()

    async def handle_submit(self, e):
        logger.info(f"Submit triggered. Processing: {self.is_processing}")
        if self.is_processing:
            return
        text = self.input_field.value
        logger.info(f"Input text: {text}")
        if not text or not text.strip():
            return

        self.input_field.value = ""
        self.is_processing = True
        self.page.update()

        self.chat_list_view.controls.append(UserMessageBubble(text.strip()))
        self.page.update()

        await self.initialize_codex()
        if not self.codex:
            logger.error("Codex init failed")
            self.is_processing = False
            self.page.update()
            return

        self.active_items = {}
        try:
            logger.info("Starting chat stream...")
            async for chunk in self.codex.chat(text.strip()):
                event_type = chunk.get("type")
                logger.debug(f"Received chunk: {event_type}")

                if event_type in ["item.started", "item.updated", "item.completed"]:
                    item_data = chunk.get("item", {})
                    item_id = item_data.get("id")
                    logger.debug(f"Item event {event_type}: {item_data}")
                    if not item_id:
                        continue

                    if item_id in self.active_items:
                        self.active_items[item_id].update_data(item_data, is_completed=(event_type == "item.completed"))
                        self.page.update()
                    else:
                        # Some providers may send item.completed without item.started.
                        widget = CodexWidgetFactory.create_widget(chunk)
                        if widget:
                            self.active_items[item_id] = widget
                            self.chat_list_view.controls.append(widget)
                            # 初始化 widget 数据
                            widget.update_data(item_data, is_completed=(event_type == "item.completed"))
                            self.page.update()
                            logger.info(f"Added widget for item {item_id} ({item_data.get('type')})")

                elif event_type in ["turn.completed", "thread.started", "error", "turn.failed"]:
                    item_id = f"sys_{event_type}_{datetime.now().timestamp()}"
                    widget = CodexWidgetFactory.create_widget(chunk)
                    if widget:
                        self.chat_list_view.controls.append(widget)
                        # 对系统事件也需要初始化数据
                        widget.update_data(chunk, is_completed=True)
                        self.page.update()

                elif event_type == "response_item":
                    # 处理 response_item 事件
                    widget = CodexWidgetFactory.create_widget(chunk)
                    if widget:
                        self.chat_list_view.controls.append(widget)
                        # 提取文本数据并初始化 widget
                        payload = chunk.get("payload", {})
                        content_list = payload.get("content", [])
                        text = ""
                        if isinstance(content_list, list):
                            for c in content_list:
                                if c.get("type") in ["text", "input_text", "output_text"]:
                                    text += c.get("text", "")
                        widget.update_data({"text": text}, is_completed=True)
                        self.page.update()

                await asyncio.sleep(0.005)
        except Exception as ex:
            logger.exception(f"Chat error: {ex}")
            self.chat_list_view.controls.append(ft.Text(f"Error: {ex}", color="red"))
        finally:
            self.is_processing = False
            self.page.update()

    async def new_conversation(self, e=None):
        if self.codex:
            await self.codex.close()
            self.codex = None
        await self.initialize_codex()
