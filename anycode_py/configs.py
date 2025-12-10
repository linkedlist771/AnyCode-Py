from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

HOME_DIR = Path.home()


## CLI COMMAND


CODEX_COMMAND = ["codex", "exec", "--json", "-"]

CODEX_ROOT_DIR = HOME_DIR / ".codex"

CODEX_SESSION_DIR = CODEX_ROOT_DIR / "sessions"

CODEX_SESSION_DIR.mkdir(exist_ok=True)


if __name__ == "__main__":
    from loguru import logger

    logger.info(f"ROOT_DIR: {ROOT_DIR}")
