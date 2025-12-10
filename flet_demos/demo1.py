"""
ChatGPT-style Desktop UI Clone built with Flet >= 0.28.3
A complete, runnable single-file application that reproduces the ChatGPT desktop app layout.
"""

import flet as ft
import pyperclip  # pip install pyperclip


# ============================================================================
# COLOR CONSTANTS
# ============================================================================
SIDEBAR_BG = "#f9f9f9"
SIDEBAR_HOVER_BG = "#ececec"
SELECTED_BG = "#e8e8e8"
MAIN_BG = "#ffffff"
BORDER_COLOR = "#e5e5e5"
TEXT_PRIMARY = "#1a1a1a"
TEXT_SECONDARY = "#6b6b6b"
ACCENT_BLUE = "#0066ff"
CODE_BG = "#f6f6f6"
USER_BUBBLE_BG = "#f0f0f0"


# ============================================================================
# SIDEBAR COMPONENTS
# ============================================================================


def create_search_box():
    """Create the search box at the top of the sidebar."""
    return ft.Container(
        content=ft.TextField(
            hint_text="Search",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=8,
            border_color=BORDER_COLOR,
            focused_border_color=TEXT_SECONDARY,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            text_size=14,
            hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=14),
        ),
        padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
    )


def create_nav_item(icon, text, has_arrow=False, on_click=None):
    """Create a navigation item with icon and text."""
    row_content = [
        ft.Icon(icon, size=18, color=TEXT_PRIMARY),
        ft.Container(width=10),
        ft.Text(text, size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.W_400),
    ]
    if has_arrow:
        row_content.append(ft.Container(expand=True))
        row_content.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=TEXT_SECONDARY))

    return ft.Container(
        content=ft.Row(row_content, spacing=0),
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_radius=8,
        on_click=on_click,
        on_hover=lambda e: setattr(e.control, "bgcolor", SIDEBAR_HOVER_BG if e.data == "true" else None)
        or e.control.update(),
    )


def create_project_item(icon, text, on_click=None):
    """Create a project item in the sidebar."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(icon, size=18, color=TEXT_SECONDARY),
                ft.Container(width=10),
                ft.Text(text, size=14, color=TEXT_PRIMARY),
            ],
            spacing=0,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=8,
        on_click=on_click,
        on_hover=lambda e: setattr(e.control, "bgcolor", SIDEBAR_HOVER_BG if e.data == "true" else None)
        or e.control.update(),
    )


def create_conversation_item(title, selected=False, has_indicator=False, on_click=None):
    """Create a conversation item in the sidebar list."""
    row_content = [
        ft.Text(
            title,
            size=14,
            color=TEXT_PRIMARY,
            overflow=ft.TextOverflow.ELLIPSIS,
            max_lines=1,
            expand=True,
        ),
    ]
    if has_indicator:
        row_content.append(
            ft.Container(
                width=8,
                height=8,
                bgcolor=ACCENT_BLUE,
                border_radius=4,
            )
        )

    return ft.Container(
        content=ft.Row(row_content, spacing=8),
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_radius=8,
        bgcolor=SELECTED_BG if selected else None,
        border=ft.border.only(left=ft.BorderSide(3, ACCENT_BLUE)) if selected else None,
        on_click=on_click,
        on_hover=lambda e: (
            setattr(
                e.control,
                "bgcolor",
                SIDEBAR_HOVER_BG if e.data == "true" and not selected else (SELECTED_BG if selected else None),
            )
            or e.control.update()
        )
        if not selected
        else None,
    )


def create_user_avatar():
    """Create the user avatar section at the bottom of the sidebar."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Text("bf", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                    width=32,
                    height=32,
                    bgcolor="#8b5cf6",
                    border_radius=16,
                    alignment=ft.alignment.center,
                ),
                ft.Container(width=10),
                ft.Text("bf", size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(12),
        border=ft.border.only(top=ft.BorderSide(1, BORDER_COLOR)),
    )


def create_sidebar():
    """Create the complete left sidebar."""
    # Conversation list items
    conversations = [
        ("TextButton 和滚动问题", True, False),
        ("TextButton 用法说明", False, True),
        ("代码实现请求", False, False),
        ("UI模型对比", False, False),
        ("2K 分辨率解释", False, False),
        ("罚球排名统计", False, False),
        ("iPhone 中毒风险分析", False, False),
        ("小说生成创新方向", False, False),
        ("小说沙盒创新方向", False, False),
        ("4090bf16 tflops 算力", False, False),
        ("情绪的神经科学解释", False, False),
    ]

    conversation_list = ft.Column(
        [create_conversation_item(title, selected, indicator) for title, selected, indicator in conversations],
        spacing=2,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=ft.Column(
            [
                # Top icons row
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.IconButton(
                                ft.Icons.GRID_VIEW_ROUNDED,
                                icon_size=20,
                                icon_color=TEXT_SECONDARY,
                            ),
                            ft.IconButton(
                                ft.Icons.EDIT_SQUARE,
                                icon_size=20,
                                icon_color=TEXT_SECONDARY,
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.only(left=8, right=4, top=4),
                ),
                # Search box
                create_search_box(),
                # Navigation items
                ft.Container(
                    content=ft.Column(
                        [
                            create_nav_item(ft.Icons.AUTO_AWESOME, "ChatGPT"),
                            create_nav_item(ft.Icons.APPS, "GPTs", has_arrow=True),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                # Divider
                ft.Container(height=8),
                # New project button
                ft.Container(
                    content=ft.Column(
                        [
                            create_nav_item(ft.Icons.ADD, "New project"),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                # Projects list
                ft.Container(
                    content=ft.Column(
                        [
                            create_project_item(ft.Icons.FOLDER_OUTLINED, "y"),
                            create_project_item(ft.Icons.FOLDER_OUTLINED, "ZemengFeng"),
                            create_project_item(ft.Icons.FOLDER_OUTLINED, "lumina"),
                            create_project_item(ft.Icons.MORE_HORIZ, "See more"),
                        ],
                        spacing=2,
                    ),
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                # Divider
                ft.Divider(height=1, color=BORDER_COLOR),
                # Conversation list (scrollable, expands)
                ft.Container(
                    content=conversation_list,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=4),
                ),
                # User avatar at bottom
                create_user_avatar(),
            ],
            spacing=0,
            expand=True,
        ),
        width=260,
        bgcolor=SIDEBAR_BG,
        border=ft.border.only(right=ft.BorderSide(1, BORDER_COLOR)),
    )


# ============================================================================
# CHAT AREA COMPONENTS
# ============================================================================


def create_header(page):
    """Create the header bar with model selector and action buttons."""

    # Model options
    models = ["ChatGPT 5.1", "ChatGPT 4o", "ChatGPT 4", "Claude 3.5 Sonnet", "GPT-3.5 Turbo"]

    selected_model = ft.Ref[ft.Text]()
    dropdown_ref = ft.Ref[ft.Dropdown]()

    def close_dropdown(e):
        dropdown_container.visible = False
        page.update()

    def select_model(model_name):
        def handler(e):
            selected_model.current.value = model_name
            dropdown_container.visible = False
            page.update()

        return handler

    def toggle_dropdown(e):
        dropdown_container.visible = not dropdown_container.visible
        page.update()

    # Create dropdown items
    dropdown_items = ft.Column(
        [
            ft.Container(
                content=ft.Text(model, size=14, color=TEXT_PRIMARY),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                on_click=select_model(model),
                on_hover=lambda e: setattr(e.control, "bgcolor", SIDEBAR_HOVER_BG if e.data == "true" else None)
                or e.control.update(),
            )
            for model in models
        ],
        spacing=0,
    )

    dropdown_container = ft.Container(
        content=dropdown_items,
        bgcolor=MAIN_BG,
        border=ft.border.all(1, BORDER_COLOR),
        border_radius=8,
        visible=False,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
        width=200,
    )

    model_selector = ft.Stack(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            "ChatGPT 5.1", size=16, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500, ref=selected_model
                        ),
                        ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=TEXT_SECONDARY),
                    ],
                    spacing=2,
                ),
                on_click=toggle_dropdown,
            ),
            ft.Container(
                content=dropdown_container,
                top=35,
                left=0,
            ),
        ]
    )

    return ft.Container(
        content=ft.Row(
            [
                # Model selector
                model_selector,
                ft.Container(expand=True),
                # Action buttons
                ft.IconButton(
                    ft.Icons.FILE_UPLOAD_OUTLINED,
                    icon_size=20,
                    icon_color=TEXT_SECONDARY,
                ),
                ft.IconButton(
                    ft.Icons.MORE_HORIZ,
                    icon_size=20,
                    icon_color=TEXT_SECONDARY,
                ),
            ]
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
    )


def create_user_message(page):
    """Create the user message bubble (aligned right) with functional edit and copy buttons."""
    message_text = """我尝试使用 TextButton，但可能还是需要查看最新的 Flet 文档。让我等待你那边的反馈，看看正确的实现方式是什么。同时，关于滚动问题，如果你能提供具体的错误信息或者行为描述，会帮助我更好地定位问题：
是否能用鼠标滚轮滚动？
是否能拖动滚动条？
是否完全无法交互（比如无法选择文字）？
这些信息能帮我更准确地找到问题所在 搜索调研下"""

    message_textfield = ft.Ref[ft.TextField]()
    message_display = ft.Ref[ft.Text]()
    edit_mode = ft.Ref[ft.Container]()
    view_mode = ft.Ref[ft.Container]()

    def copy_message(e):
        try:
            pyperclip.copy(message_text)
            # Show a brief confirmation (you could add a snackbar here)
            e.control.icon = ft.Icons.CHECK
            page.update()
            # Reset icon after 1 second
            import time

            time.sleep(1)
            e.control.icon = ft.Icons.CONTENT_COPY_OUTLINED
            page.update()
        except:
            pass

    def edit_message(e):
        view_mode.current.visible = False
        edit_mode.current.visible = True
        message_textfield.current.value = message_text
        page.update()

    def save_edit(e):
        # In a real app, you would save the edited message
        view_mode.current.visible = True
        edit_mode.current.visible = False
        message_display.current.value = message_textfield.current.value
        page.update()

    def cancel_edit(e):
        view_mode.current.visible = True
        edit_mode.current.visible = False
        page.update()

    return ft.Container(
        content=ft.Column(
            [
                # Message bubble - view mode
                ft.Container(
                    ref=view_mode,
                    content=ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            message_text,
                                            size=14,
                                            color=TEXT_PRIMARY,
                                            selectable=True,
                                            ref=message_display,
                                        ),
                                    ]
                                ),
                                bgcolor=USER_BUBBLE_BG,
                                border_radius=16,
                                padding=ft.padding.all(16),
                                width=600,
                            ),
                        ]
                    ),
                ),
                # Message bubble - edit mode
                ft.Container(
                    ref=edit_mode,
                    visible=False,
                    content=ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.TextField(
                                            ref=message_textfield,
                                            multiline=True,
                                            min_lines=5,
                                            max_lines=10,
                                            border_color=BORDER_COLOR,
                                            text_size=14,
                                        ),
                                        ft.Row(
                                            [
                                                ft.Container(expand=True),
                                                ft.TextButton("Cancel", on_click=cancel_edit),
                                                ft.ElevatedButton("Save", on_click=save_edit),
                                            ],
                                            spacing=8,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                bgcolor=USER_BUBBLE_BG,
                                border_radius=16,
                                padding=ft.padding.all(16),
                                width=600,
                            ),
                        ]
                    ),
                ),
                # Action buttons below message
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.IconButton(
                            ft.Icons.EDIT_OUTLINED,
                            icon_size=16,
                            icon_color=TEXT_SECONDARY,
                            on_click=edit_message,
                            tooltip="Edit message",
                        ),
                        ft.IconButton(
                            ft.Icons.CONTENT_COPY_OUTLINED,
                            icon_size=16,
                            icon_color=TEXT_SECONDARY,
                            on_click=copy_message,
                            tooltip="Copy message",
                        ),
                    ]
                ),
            ],
            spacing=4,
        ),
        padding=ft.padding.only(left=60, right=20, top=20, bottom=10),
    )


def create_code_block(code_text, language="python"):
    """Create a styled code block with copy button."""

    def copy_code(e):
        try:
            pyperclip.copy(code_text)
            e.control.content.controls[1].value = "Copied!"
            e.control.update()
            import time

            time.sleep(1)
            e.control.content.controls[1].value = "Copy"
            e.control.update()
        except:
            pass

    return ft.Container(
        content=ft.Column(
            [
                # Header bar with language and copy button
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(language, size=12, color=TEXT_SECONDARY),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CONTENT_COPY, size=14, color=TEXT_SECONDARY),
                                        ft.Text("Copy", size=12, color=TEXT_SECONDARY),
                                    ],
                                    spacing=4,
                                ),
                                on_click=copy_code,
                                on_hover=lambda e: setattr(
                                    e.control, "bgcolor", SIDEBAR_HOVER_BG if e.data == "true" else None
                                )
                                or e.control.update(),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                            ),
                        ]
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border=ft.border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
                ),
                # Code content
                ft.Container(
                    content=ft.Text(
                        code_text,
                        size=13,
                        font_family="monospace",
                        color=TEXT_PRIMARY,
                        selectable=True,
                    ),
                    padding=ft.padding.all(12),
                ),
            ],
            spacing=0,
        ),
        bgcolor=CODE_BG,
        border_radius=8,
        border=ft.border.all(1, BORDER_COLOR),
    )


def create_assistant_message(page):
    """Create the assistant message block (aligned left) with clickable thought area."""
    code_example = """ft.Text(
    "Selectable plain text with default style",
    selectable=True,
)"""

    thought_expanded = ft.Ref[ft.Column]()
    thought_icon = ft.Ref[ft.Icon]()

    def toggle_thought(e):
        if thought_expanded.current.visible:
            thought_expanded.current.visible = False
            thought_icon.current.name = ft.Icons.CHEVRON_RIGHT
        else:
            # Show dialog/popup
            show_thought_dialog(page)
        page.update()

    def show_thought_dialog(page):
        dlg = ft.AlertDialog(
            title=ft.Text("Thought Process (47s)", size=18, weight=ft.FontWeight.W_600),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Analysis Steps:", size=14, weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Text("1. Understanding the user's question about TextButton and scrolling issues", size=13),
                        ft.Container(height=4),
                        ft.Text("2. Researching Flet documentation for text selection capabilities", size=13),
                        ft.Container(height=4),
                        ft.Text("3. Identifying the selectable parameter in Text widget", size=13),
                        ft.Container(height=4),
                        ft.Text("4. Preparing code examples and explanations", size=13),
                        ft.Container(height=4),
                        ft.Text("5. Structuring the response with clear sections", size=13),
                        ft.Container(height=16),
                        ft.Text("Sources Consulted:", size=14, weight=ft.FontWeight.W_500),
                        ft.Container(height=8),
                        ft.Text("🔵 Flet official documentation", size=13),
                        ft.Text("🟡 Python API reference", size=13),
                        ft.Text("🔴 Community examples", size=13),
                        ft.Text("🟠 GitHub issues and discussions", size=13),
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=400,
                width=500,
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: page.close(dlg)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg)

    return ft.Container(
        content=ft.Column(
            [
                # Thought header (clickable)
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Thought for 47s", size=13, color=TEXT_SECONDARY),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, size=16, color=TEXT_SECONDARY, ref=thought_icon),
                        ],
                        spacing=4,
                    ),
                    on_click=toggle_thought,
                    ink=True,
                ),
                # Expanded thought (hidden by default)
                ft.Column(
                    [
                        ft.Container(height=8),
                        ft.Text("Detailed thinking process...", size=12, color=TEXT_SECONDARY, italic=True),
                    ],
                    ref=thought_expanded,
                    visible=False,
                ),
                ft.Container(height=8),
                # Sources row
                ft.Row(
                    [
                        ft.Text("🔵", size=14),
                        ft.Text("🟡", size=14),
                        ft.Text("🔴", size=14),
                        ft.Text("🟠", size=14),
                        ft.Container(width=4),
                        ft.Text("Sources", size=13, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ],
                    spacing=2,
                ),
                ft.Container(height=16),
                # Main content
                ft.Text(
                    "先直接把几个关键点说清楚：",
                    size=15,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                    selectable=True,
                ),
                ft.Container(height=16),
                # Section heading
                ft.Text(
                    "1. Text 到底能不能交互 / 复制?",
                    size=16,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                    selectable=True,
                ),
                ft.Container(height=12),
                # Subheading
                ft.Text(
                    "默认行为",
                    size=14,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                    selectable=True,
                ),
                ft.Container(height=8),
                # Bullet point
                ft.Row(
                    [
                        ft.Text("•", size=14, color=TEXT_PRIMARY),
                        ft.Container(width=8),
                        ft.Column(
                            [
                                ft.Text(
                                    "Flet 里的大部分控件默认都是不可选中的，包括 Text。",
                                    size=14,
                                    color=TEXT_PRIMARY,
                                    selectable=True,
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            '所以你现在看到 "文字不能选、不能复制"，大概率是因为用的是默认配置。',
                                            size=14,
                                            color=TEXT_PRIMARY,
                                            selectable=True,
                                        ),
                                        ft.Container(
                                            content=ft.Text("flet.dev +1", size=11, color=TEXT_SECONDARY),
                                            bgcolor="#f0f0f0",
                                            border_radius=4,
                                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        ),
                                    ],
                                    spacing=8,
                                    wrap=True,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=16),
                # Another subheading
                ft.Text(
                    "让 Text 可选 & 可复制",
                    size=14,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                    selectable=True,
                ),
                ft.Container(height=8),
                # Numbered item
                ft.Row(
                    [
                        ft.Text("1.", size=14, color=TEXT_PRIMARY),
                        ft.Container(width=8),
                        ft.Text(
                            "直接把 Text 变成可选：",
                            size=14,
                            color=TEXT_PRIMARY,
                            selectable=True,
                        ),
                    ]
                ),
                ft.Container(height=12),
                # Code block
                create_code_block(code_example, "python"),
                ft.Container(height=8),
                # Scroll down indicator
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=20, color=TEXT_SECONDARY),
                            width=32,
                            height=32,
                            bgcolor=MAIN_BG,
                            border_radius=16,
                            border=ft.border.all(1, BORDER_COLOR),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(expand=True),
                    ]
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.only(left=20, right=60, top=10, bottom=20),
    )


def create_chat_area(page):
    """Create the scrollable chat conversation area."""
    return ft.Container(
        content=ft.Column(
            [
                create_user_message(page),
                create_assistant_message(page),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
    )


def create_input_bar(page: ft.Page):
    """Create the bottom input bar with all buttons inside."""

    # Input text field reference
    input_field_ref = ft.Ref[ft.TextField]()

    def on_send_click(e):
        """Handle send button click."""
        if input_field_ref.current and input_field_ref.current.value and input_field_ref.current.value.strip():
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"Message sent: {input_field_ref.current.value[:50]}..."), bgcolor="#4caf50"
                )
            )
            input_field_ref.current.value = ""
            page.update()

    def on_attach_click(e):
        """Handle attachment button click."""
        page.open(ft.SnackBar(content=ft.Text("Attachment feature - select files"), bgcolor=ACCENT_BLUE))

    def on_web_click(e):
        """Handle web search button click."""
        page.open(ft.SnackBar(content=ft.Text("Web search enabled"), bgcolor=ACCENT_BLUE))

    def on_deep_think_click(e):
        """Handle deep think button click."""
        page.open(ft.SnackBar(content=ft.Text("Deep thinking mode activated"), bgcolor=ACCENT_BLUE))

    def on_code_click(e):
        """Handle code button click."""
        page.open(ft.SnackBar(content=ft.Text("Code interpreter enabled"), bgcolor=ACCENT_BLUE))

    def on_canvas_click(e):
        """Handle canvas button click."""
        page.open(ft.SnackBar(content=ft.Text("Canvas mode - create visual content"), bgcolor=ACCENT_BLUE))

    def on_camera_click(e):
        """Handle camera button click."""
        page.open(ft.SnackBar(content=ft.Text("Camera - capture image"), bgcolor=ACCENT_BLUE))

    def on_mic_click(e):
        """Handle microphone button click."""
        page.open(ft.SnackBar(content=ft.Text("Voice input - speak now"), bgcolor=ACCENT_BLUE))

    # Input text field
    input_field = ft.TextField(
        ref=input_field_ref,
        hint_text="Ask anything",
        border=ft.InputBorder.NONE,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=12),
        text_size=14,
        hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=14),
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=5,
        on_submit=on_send_click,  # Support Enter key
    )

    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                [
                    # Text input area
                    ft.Container(
                        content=input_field,
                        padding=ft.padding.only(left=8, right=8, top=4),
                    ),
                    # Bottom row with all buttons
                    ft.Container(
                        content=ft.Row(
                            [
                                # Left side buttons
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            ft.Icons.ADD,
                                            icon_size=20,
                                            icon_color=TEXT_SECONDARY,
                                            tooltip="Attach files",
                                            on_click=on_attach_click,
                                        ),
                                        ft.IconButton(
                                            ft.Icons.LANGUAGE,
                                            icon_size=20,
                                            icon_color=TEXT_SECONDARY,
                                            tooltip="Web search",
                                            on_click=on_web_click,
                                        ),
                                        ft.IconButton(
                                            ft.Icons.BOLT,
                                            icon_size=20,
                                            icon_color=TEXT_SECONDARY,
                                            tooltip="Deep think",
                                            on_click=on_deep_think_click,
                                        ),
                                        ft.IconButton(
                                            ft.Icons.CODE,
                                            icon_size=20,
                                            icon_color=TEXT_SECONDARY,
                                            tooltip="Code",
                                            on_click=on_code_click,
                                        ),
                                        ft.IconButton(
                                            ft.Icons.AUTO_FIX_HIGH,
                                            icon_size=20,
                                            icon_color=TEXT_SECONDARY,
                                            tooltip="Canvas",
                                            on_click=on_canvas_click,
                                        ),
                                        # Model indicator
                                        ft.Container(
                                            content=ft.Text("5.1", size=12, color=TEXT_SECONDARY),
                                            bgcolor="#f0f0f0",
                                            border_radius=8,
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                                # Spacer
                                ft.Container(expand=True),
                                # Right side buttons
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Icon(
                                                ft.Icons.CAMERA_ALT_OUTLINED, size=18, color=TEXT_SECONDARY
                                            ),
                                            width=36,
                                            height=36,
                                            bgcolor="#f0f0f0",
                                            border_radius=18,
                                            alignment=ft.alignment.center,
                                            on_click=on_camera_click,
                                            tooltip="Camera",
                                        ),
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.MIC_NONE, size=18, color=TEXT_SECONDARY),
                                            width=36,
                                            height=36,
                                            bgcolor="#f0f0f0",
                                            border_radius=18,
                                            alignment=ft.alignment.center,
                                            on_click=on_mic_click,
                                            tooltip="Voice input",
                                        ),
                                        # Send button with up arrow icon
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.ARROW_UPWARD, size=18, color=ft.Colors.WHITE),
                                            width=36,
                                            height=36,
                                            bgcolor="#1a1a1a",
                                            border_radius=18,
                                            alignment=ft.alignment.center,
                                            on_click=on_send_click,
                                            tooltip="Send message",
                                        ),
                                    ],
                                    spacing=8,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=4, right=8, bottom=8),
                    ),
                ],
                spacing=0,
            ),
            bgcolor="#f9f9f9",
            border_radius=24,
            border=ft.border.all(1, BORDER_COLOR),
        ),
        padding=ft.padding.only(left=20, right=20, bottom=16, top=8),
        bgcolor=MAIN_BG,
    )


def create_main_chat_area(page: ft.Page):
    """Create the complete right-side chat area."""
    return ft.Container(
        content=ft.Column(
            [
                create_header(page),
                create_chat_area(page),
                create_input_bar(page),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=MAIN_BG,
    )


# ============================================================================
# MAIN APP
# ============================================================================


def main(page: ft.Page):
    """Main entry point for the Flet app."""
    # Page configuration
    page.title = "ChatGPT Clone"
    page.bgcolor = MAIN_BG
    page.padding = 0
    page.spacing = 0
    page.window.width = 1280
    page.window.height = 720
    page.window.min_width = 800
    page.window.min_height = 600

    # Main layout: sidebar + chat area
    main_layout = ft.Row(
        [
            create_sidebar(),
            create_main_chat_area(page),
        ],
        spacing=0,
        expand=True,
    )

    page.add(main_layout)


# Run the app
if __name__ == "__main__":
    ft.app(target=main)
