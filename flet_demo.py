from dotenv import load_dotenv

load_dotenv()

from anycode_py.ui.app import main as anycode_py_main
import flet as ft


if __name__ == "__main__":
    ft.app(target=anycode_py_main)
