import json
from typing import Any, AsyncGenerator

from .base import BaseProcessManager
from ..configs import CODEX_COMMAND

from pathlib import Path
from loguru import logger


class CodexProcessManager(BaseProcessManager):
    def __init__(self, *, env: dict[str, str] | None = None, cwd: Path | None = Path.cwd()):
        super().__init__(CODEX_COMMAND, env=env, cwd=cwd)
        self.current_session_id: str | None = None

    @classmethod
    async def create(cls, *, env: dict[str, str] | None = None, cwd: Path | None = Path.cwd()) -> "CodexProcessManager":
        self = cls(env=env, cwd=cwd)
        await self._init_async()
        return self

    async def send(self, text: str, close_stdin: bool = True):
        await super().send(text, close_stdin)

    async def chat(self, prompt: str) -> AsyncGenerator[Any, None]:
        if self.current_session_id:
            await self.resume()
        await self.send(prompt)
        async for data_chunk in self.read_stream():
            # session id will be recored by default, and each process manger corresponds to
            # one conversation, when handle, different, it will need to switch.
            self.current_session_id = data_chunk.get("thread_id", "") or self.current_session_id
            yield data_chunk

    async def resume(self, session_id: str | None = None, prompt: str | None = None):
        if not session_id:
            logger.info(f"session_id is not provided, using current session_id: {self.current_session_id}")
            session_id = self.current_session_id
            if not session_id:
                raise ValueError("session_id is required to resume a session")

        # Stop any existing process before restarting in resume mode
        await self.close()

        # Build resume command: codex exec --json resume <session_id> -
        # self.cmd = ["codex", "exec", "--json", "resume", session_id, "-"]
        # CODEX_COMMAND = ["codex", "exec", "--json", "-"]

        self.cmd = [*CODEX_COMMAND[:-1], "resume", session_id, CODEX_COMMAND[-1]]
        # Launch resumed process
        await self._init_async()

        # Optionally send a new prompt to the resumed session
        if prompt:
            # suffix = "" if prompt.endswith("\n") else "\n"
            await self.send(prompt, close_stdin=True)
