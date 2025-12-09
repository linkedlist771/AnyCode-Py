import json
from dotenv import load_dotenv
load_dotenv()
from anycode_py.process_manager.codex import CodexProcessManager
from loguru import logger 

async def main():
    codex = await CodexProcessManager.create()
    session_id = None
    async for line in codex.chat("当前路径是什么?!"):
        logger.debug(line)
        session_id = line.get("thread_id", "") or session_id
    if session_id:
        await codex.resume(session_id)

    async for line in codex.chat("我上一句问你了你什么?!"):
        logger.debug(line)
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())