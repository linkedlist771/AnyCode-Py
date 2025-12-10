import os
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import json
from typing import AsyncGenerator, Any
from loguru import logger
from pathlib import Path


class BaseProcessManager:
    def __init__(self, cmd, *, env=None, cwd: Path | None = None):
        self.cmd = cmd
        self.env = {**os.environ, **(env or {})}
        self.proc: asyncio.subprocess.Process | None = None
        self.cwd = cwd

    @classmethod
    async def create(cls, cmd, *, env=None, cwd: Path | None = None) -> "BaseProcessManager":
        self = cls(cmd, env=env, cwd=cwd)
        await self._init_async()
        return self

    async def _init_async(self):
        self.proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
            env=self.env,
            cwd=self.cwd,
        )

    async def send(self, text: str, close_stdin: bool = False):
        if self.proc is None or self.proc.stdin is None:
            raise RuntimeError("Process not initialized or stdin closed")
        self.proc.stdin.write(text.encode())
        await self.proc.stdin.drain()
        if close_stdin:
            self.proc.stdin.close()
            await self.proc.stdin.wait_closed()

    async def read_stream(self) -> AsyncGenerator[Any, None]:
        if self.proc is None or self.proc.stdout is None:
            raise RuntimeError("Process not initialized")
        async for line in self.proc.stdout:
            line_str = line.decode().strip()
            if not line_str:
                continue
            try:
                yield json.loads(line_str)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e}, line: {line_str}")

    @property
    def is_running(self) -> bool:
        return self.proc is not None and self.proc.returncode is None

    async def close(self, timeout: float = 5.0):
        if self.proc is None:
            return
        if self.proc.stdin is not None and not self.proc.stdin.is_closing():
            self.proc.stdin.close()
            try:
                await self.proc.stdin.wait_closed()
            except Exception:
                pass
        try:
            await asyncio.wait_for(self.proc.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Process didn't exit in {timeout}s, killing...")
            self.proc.kill()
            await self.proc.wait()
        except ProcessLookupError:
            pass

    async def __aenter__(self) -> "BaseProcessManager":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
        return None
