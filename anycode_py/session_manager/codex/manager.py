from pathlib import Path
from typing import Dict, List, Optional
import json

from anycode_py.configs import CODEX_SESSION_DIR

from functools import lru_cache

from anycode_py.utils.jsonl_utis import load_jsonl


@lru_cache
def _find_all_session_jsonl_path() -> List[Path]:
    paths = list(CODEX_SESSION_DIR.rglob("*.jsonl"))
    # p.stat().st_mtime 获取文件的最后修改时间戳
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def _extract_session_id(session_jsonl_path: Path) -> str:
    filename = session_jsonl_path.stem  # 去掉 .jsonl 扩展名
    parts = filename.split("-")
    if len(parts) >= 5:
        uuid = "-".join(parts[-5:])
        return uuid
    logger.warning(f"Failed to extract session_id from {session_jsonl_path}")


class CodexSessionManager(object):
    """Codex 会话管理器 - 懒加载设计"""

    def __init__(self) -> None:
        self.session_jsonl_path = _find_all_session_jsonl_path()
        self.session_id_map = {path: _extract_session_id(path) for path in self.session_jsonl_path}
        self._cache: Dict[str, List[Dict]] = {}

    def load_session(self, session_id: str) -> Optional[List[Dict]]:
        if session_id in self._cache:
            return self._cache[session_id]
        target_path = None
        for json_path in self.session_jsonl_path:
            if session_id in str(json_path):
                target_path = json_path
                break

        if not target_path:
            return None
        try:
            session_data = load_jsonl(target_path)
            self._cache[session_id] = session_data
            return session_data

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    def get_session_list(self, start: int = 0, end: Optional[int] = None) -> List[Dict]:
        end = end or len(self.session_jsonl_path)
        selected_paths = self.session_jsonl_path[start:end]
        result = []
        for path in selected_paths:
            result.append(
                {
                    "session_id": self.session_id_map[path],
                    "path": str(path),
                    "modified_time": path.stat().st_mtime,
                    "size": path.stat().st_size,
                }
            )

        return result

    def clear_cache(self) -> None:
        self._cache.clear()

    def get_total_sessions(self) -> int:
        return len(self.session_jsonl_path)


if __name__ == "__main__":
    from loguru import logger

    codex_session_manager = CodexSessionManager()

    logger.info(f"Total sessions: {codex_session_manager.get_total_sessions()}")

    # 显示所有会话路径
    for i, path in enumerate(codex_session_manager.session_jsonl_path[:10]):  # 只显示前10个
        logger.debug(f"[{i}] {path}")

    # 获取会话列表（仅元数据）
    session_list = codex_session_manager.get_session_list(0, 5)
    logger.info(f"Session list (0-5): {session_list}")

    # 加载特定会话
    if codex_session_manager.session_jsonl_path:
        first_session_id = codex_session_manager.session_jsonl_path[0].stem
        session_data = codex_session_manager.load_session(first_session_id)
        logger.info(f"Loaded session {first_session_id}, records: {len(session_data) if session_data else 0}")
