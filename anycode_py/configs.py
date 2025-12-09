from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent





## CLI COMMAND 


CODEX_COMMAND = ["codex", "exec", "--json", "-"]



if __name__ == "__main__":
    from loguru import logger
    logger.info(f"ROOT_DIR: {ROOT_DIR}")