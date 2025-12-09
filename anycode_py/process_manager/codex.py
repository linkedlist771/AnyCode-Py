"""Process manager specialized for the `codex` CLI."""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator

from .base import BaseProcessManager
from ..configs import CODEX_COMMAND

from pathlib import Path


class CodexProcessManager(BaseProcessManager):
    """Convenience wrapper around BaseProcessManager with the codex command."""

    def __init__(self, *, env: dict[str, str] | None = None, cwd: Path | None = Path.cwd()):
        super().__init__(CODEX_COMMAND, env=env, cwd=cwd)

    @classmethod
    async def create(cls, *, env: dict[str, str] | None = None, cwd: Path | None = Path.cwd()) -> "CodexProcessManager":
        self = cls(env=env, cwd=cwd)
        await self._init_async()
        return self

    async def send(self, text: str, close_stdin: bool = True):
        await super().send(text, close_stdin)


    async def chat(self, prompt: str) -> AsyncGenerator[Any, None]:
        await self.send(prompt)
        async for line in self.read_stream():
            yield line


    async def resume(self, session_id: str, prompt: str | None = None):
        if not session_id:
            raise ValueError("session_id is required to resume a session")

        # Stop any existing process before restarting in resume mode
        await self.close()

        # Build resume command: codex exec --json resume <session_id> -
        # self.cmd = ["codex", "exec", "--json", "resume", session_id, "-"]
        # CODEX_COMMAND = ["codex", "exec", "--json", "-"]

        self.cmd = [ *CODEX_COMMAND[:-1], "resume", session_id, CODEX_COMMAND[-1]]
        # Launch resumed process
        await self._init_async()

        # Optionally send a new prompt to the resumed session
        if prompt:
            # suffix = "" if prompt.endswith("\n") else "\n"
            await self.send(prompt, close_stdin=True)


    