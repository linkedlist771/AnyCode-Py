from pathlib import Path
from typing import Dict, List, Optional
from collections import OrderedDict
import json
from loguru import logger
from anycode_py.configs import CODEX_SESSION_DIR

from functools import lru_cache
import ast
from anycode_py.utils.jsonl_utis import load_jsonl


@lru_cache
def _find_all_session_jsonl_path() -> List[Path]:
    paths = list(CODEX_SESSION_DIR.rglob("*.jsonl"))
    # p.stat().st_mtime 获取文件的最后修改时间戳
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)


def _extract_text_from_message(message: str | List) -> str:
    text = message
    if isinstance(message, List):
        text = text[0].get("text", str(text))
    elif isinstance(message, str):
        try:
            _text = ast.literal_eval(message)
            text = _text[0].get("text", str(_text))
        except Exception as e:
            # logger.error(e)
            pass
    return text


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
        # Simple LRU cache with max size 20 to cap memory usage.
        self._cache: "OrderedDict[str, List[Dict]]" = OrderedDict()
        self._cache_limit = 20

    def load_session(self, session_id: str) -> Optional[List[Dict]]:
        if session_id in self._cache:
            # Touch the key to mark it as recently used.
            self._cache.move_to_end(session_id)
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
            self._cache.move_to_end(session_id)
            if len(self._cache) > self._cache_limit:
                # Evict least recently used
                self._cache.popitem(last=False)
            return session_data

        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None

    # {"timestamp":"2025-12-10T05:10:17.795Z","type":"session_meta","payload":{"id":"019b06aa-d59e-79a1-8d46-96c7c5dd63ca","timestamp":"2025-12-10T05:10:17.758Z","cwd":"/Users/a1234/Desktop/GithubProjects/AnyCode-Py","originator":"codex_exec","cli_version":"0.61.0","instructions":null,"source":"exec","model_provider":"openai","git":{"commit_hash":"e406c5b485606093e086e6b35f4471d08c9d28f5","branch":"main","repository_url":"https://github.com/linkedlist771/AnyCode-Py.git"}}}
    # {"timestamp":"2025-12-10T05:10:17.795Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"<environment_context>\n  <cwd>/Users/a1234/Desktop/GithubProjects/AnyCode-Py</cwd>\n  <approval_policy>never</approval_policy>\n  <sandbox_mode>workspace-write</sandbox_mode>\n  <network_access>restricted</network_access>\n  <shell>zsh</shell>\n</environment_context>"}]}}
    # {"timestamp":"2025-12-10T05:10:17.804Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"你好你是什么模型？"}]}}
    # {"timestamp":"2025-12-10T05:10:17.804Z","type":"event_msg","payload":{"type":"user_message","message":"你好你是什么模型？","images":[]}}
    # {"timestamp":"2025-12-10T05:10:17.809Z","type":"turn_context","payload":{"cwd":"/Users/a1234/Desktop/GithubProjects/AnyCode-Py","approval_policy":"never","sandbox_policy":{"type":"workspace-write","network_access":false,"exclude_tmpdir_env_var":false,"exclude_slash_tmp":false},"model":"gpt-5.1-codex-max","effort":"xhigh","summary":"auto"}}
    # {"timestamp":"2025-12-10T05:10:17.995Z","type":"response_item","payload":{"type":"ghost_snapshot","ghost_commit":{"id":"14b7751f24b5e01e6eb648a912efedf8d0007cc3","parent":"e406c5b485606093e086e6b35f4471d08c9d28f5","preexisting_untracked_files":["anycode_py/ui/__init__.py","anycode_py/ui/base.py","anycode_py/ui/codex.py","flet_chat/__init__.py","flet_chat/app.py","flet_chat/main.py","flet_chat/styles.py","flet_chat/widgets/__init__.py","flet_chat/widgets/action_widgets.py","flet_chat/widgets/advanced_widgets.py","flet_chat/widgets/base.py","flet_chat/widgets/factory.py","flet_chat/widgets/message_bubbles.py","flet_demo.py","flet_demos/demo1.py",".env"],"preexisting_untracked_dirs":[".venv","anycode_py/__pycache__","anycode_py/process_manager/__pycache__","flet_chat/__pycache__","flet_chat/widgets/__pycache__"]}}}
    # {"timestamp":"2025-12-10T05:10:19.095Z","type":"event_msg","payload":{"type":"token_count","info":null,"rate_limits":{"primary":null,"secondary":null,"credits":null}}}
    # {"timestamp":"2025-12-10T05:10:24.778Z","type":"event_msg","payload":{"type":"agent_reasoning","text":"**Providing concise identity response**\n\nI'll confirm that ChatGPT is a large language model based on GPT-4 from OpenAI, answering briefly in Chinese as requested."}}
    # {"timestamp":"2025-12-10T05:10:25.108Z","type":"event_msg","payload":{"type":"agent_message","message":"你好，我是 ChatGPT，一个由 OpenAI 训练的大型语言模型。"}}
    # {"timestamp":"2025-12-10T05:10:25.110Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":3078,"cached_input_tokens":2048,"output_tokens":22,"reasoning_output_tokens":0,"total_tokens":3100},"last_token_usage":{"input_tokens":3078,"cached_input_tokens":2048,"output_tokens":22,"reasoning_output_tokens":0,"total_tokens":3100},"model_context_window":258400},"rate_limits":{"primary":null,"secondary":null,"credits":null}}}
    # {"timestamp":"2025-12-10T05:10:25.111Z","type":"response_item","payload":{"type":"reasoning","summary":[{"type":"summary_text","text":"**Providing concise identity response**\n\nI'll confirm that ChatGPT is a large language model based on GPT-4 from OpenAI, answering briefly in Chinese as requested."}],"content":null,"encrypted_content":"gAAAAABpOQDA9gsc02VvG6rT2oYzcIMbbMMj2tlsePllliQxhP9CAspmZPiFh4eTA53onp-3UGVEW8glqy531nfvCTmLDhfmtQCvpmFb71oP1d3KVMEx7Y0iOfDrRc2jHmHczK5aL9GBG6OZVtYak5zSenrAGzzMt4jV1UTOHUME2CZ7r0W2zD8O4xCbmJGC3vnQ59Cz52VWO2uQqXshd9LatSo2o3k_f3N-0PTvIWIrPMJj7aJrlx7lPST2yAI72XJlaQw6YVxq7dGCVQ2Xe-i9RzZT_dNRJD0HlWVS8NcNfEciXdzOJP-2KhYIzH4IJcc1i0w_ld4Ex8hREHT5faKZLTSGp_emsg5wM3qvf8QqiNCgiG-1vI8iNZouwXPQDEUr7wDJiRcPJaRp4eFAi0-bEvUGTYglsHVrIIAfOGmJdB_0ND-CnqVY4f6EmdeoRIhm3iRfvqriP3cZHRG7DVepi1cuR__hx5FGs5zLoYpl5MRoJcM3lIq2jcen_dx0GHBYmMwTq9xarca8qZpkk8yAb6-A_SD9sxq1YDJT6AwR8vVsj8zrP7IW2OQ1CYxMuB7So4xrAL3GqUY2wMm_m6vf1zZW3DxqCUjpgDpLPX16SH3kIW44O2FRcAzm4Mespt3ufmrFw3raaSYewYmtvyO1DFLcEuBF6QK0QgvPryObpXgb3a7wZ-xjHVSBF2usavtqqxu_o8wWwukeVaKivEtdlei5Yfv5BkZzoxKPL-3mA0EYN6HCjGZasKW6dzs4b_GcCL3bhLJf2c78hh19FMNd-hFaOKlOisOYuHbo1J8IaytIASshFTj1uvBC34Kt9WNQlBIc1T3-Smlj1DhZ_BI3kwbIv68eOqq8Yf-A_D2--zbNdxYykZQIj2ihkpjAGwOeOjoIzyVGKl1sfPfQLaY7CWiegWoZF4j_InN-Oh2XPNUY5lKUnbYI4C-wJHphCfs-xD4UT-xrlXW4AeKt49KXb3MhBgZMCdXIgltn8YDG1pO1hR7Ot3X_weczfue-CVI1gu7ec6Cq8jsdz9X-rplTr4sLnm4fumWfmthDA94rn2sciOP5084bkkTxYJpS4T_nhgCxhmwV"}}
    # {"timestamp":"2025-12-10T05:10:25.112Z","type":"response_item","payload":{"type":"message","role":"assistant","content":[{"type":"output_text","text":"你好，我是 ChatGPT，一个由 OpenAI 训练的大型语言模型。"}]}}
    # {"timestamp":"2025-12-10T05:10:33.387Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"看看我系统运行情况？"}]}}
    # {"timestamp":"2025-12-10T05:10:33.388Z","type":"event_msg","payload":{"type":"user_message","message":"看看我系统运行情况？","images":[]}}
    # {"timestamp":"2025-12-10T05:10:33.388Z","type":"turn_context","payload":{"cwd":"/Users/a1234/Desktop/GithubProjects/AnyCode-Py","approval_policy":"never","sandbox_policy":{"type":"workspace-write","network_access":false,"exclude_tmpdir_env_var":false,"exclude_slash_tmp":false},"model":"gpt-5.1-codex-max","effort":"xhigh","summary":"auto"}}
    # {"timestamp":"2025-12-10T05:10:33.592Z","type":"response_item","payload":{"type":"ghost_snapshot","ghost_commit":{"id":"7ebaca45748df0d007c0237d237e6eeeddab3768","parent":"e406c5b485606093e086e6b35f4471d08c9d28f5","preexisting_untracked_files":["anycode_py/ui/__init__.py","anycode_py/ui/base.py","anycode_py/ui/codex.py","flet_chat/__init__.py","flet_chat/app.py","flet_chat/main.py","flet_chat/styles.py","flet_chat/widgets/__init__.py","flet_chat/widgets/action_widgets.py","flet_chat/widgets/advanced_widgets.py","flet_chat/widgets/base.py","flet_chat/widgets/factory.py","flet_chat/widgets/message_bubbles.py","flet_demo.py","flet_demos/demo1.py",".env"],"preexisting_untracked_dirs":[".venv","anycode_py/__pycache__","anycode_py/process_manager/__pycache__","flet_chat/__pycache__","flet_chat/widgets/__pycache__"]}}}
    # {"timestamp":"2025-12-10T05:10:34.609Z","type":"event_msg","payload":{"type":"token_count","info":null,"rate_limits":{"primary":null,"secondary":null,"credits":null}}}
    # {"timestamp":"2025-12-10T05:10:43.658Z","type":"event_msg","payload":{"type":"agent_reasoning","text":"**Preparing system status commands**\n\nI'm setting up safe shell commands to gather system info like kernel details, uptime, disk usage, and memory stats within the user's workspace for a summary report."}}
    # {"timestamp":"2025-12-10T05:10:44.231Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":3110,"cached_input_tokens":2048,"output_tokens":334,"reasoning_output_tokens":256,"total_tokens":3444},"last_token_usage":{"input_tokens":3110,"cached_input_tokens":2048,"output_tokens":334,"reasoning_output_tokens":256,"total_tokens":3444},"model_context_window":258400},"rate_limits":{"primary":null,"secondary":null,"credits":null}}}
    # {"timestamp":"2025-12-10T05:10:44.323Z","type":"response_item","payload":{"type":"reasoning","summary":[{"type":"summary_text","text":"**Preparing system status commands**\n\nI'm setting up safe shell commands to gather system info like kernel details, uptime, disk usage, and memory stats within the user's workspace for a summary report."}],"content":null,"encrypted_content":"gAAAAABpOQDT_X0nJg4UnqlBHtZiU7gmmT14VJXrW3oWf6z0-IRxx__DlPxDud-ZeGILEUnmiovg1NjodoA-URXoYA1-_5Zune-52pPYr-RxhD04aHtN-AVXmKEsXJJUxLvmWJviHYDKmQG4yOAetcU4lO9PEGlcOFaKCW1bL8qUVO3mKgs865QsiHHtDMFlufwwHhuuVGT3eq4-eJwRrqIX-xj-4HMvX0BU6L0nSUjUkgveeGZQNyiajgiMaVnJd9vHpiMR3VrS9ktokXhRt-pwMEcG3CF2BY-Zo0EVF1m57MoOUwQ9DsWQ03eyQZ04MUQFwyvQilU4V60ImNeMKzmEiCg75K-6mnbLJeA0oB0fU_NROWem_dXARMJqzprqY74rCMKNZpHdDYuRRRkok5movy1gi7mtkSICkeO6nWNOJBLrxY3y3B1TzQj5zy1CuB2yt-IS_C6P7L4SRbmud2Y9RWuM5EK89BDGXxbGmI2967i-PnrT4ni7KS3RTiHfLmMpThLj4xx-DmtnuobocKBz3waG0jY6JlFXztAY7DEj6Uj0NKdjSKZ4t3djdvbV713ZbombBVpbjxpElAv8MnUxFtTkh-VEkCDxooDFFW9IDTtKn6iC71OD6IdNCmsT0dTPEMBb5HUV45kNjeSicdhHjTOw3gsowVQ_0SJhCydT8BUwEMr6RwJIj5o3xGdeDrxX9yyPDabZKXJGE9XguyBWh_1f4SOSg2rfBPdbwLAajXyKKV9RyXGjenfqgbeVzVGXu5_K44zZDVZSUVuV2_rUY9OE_0wgxwI5nEGUhWU0nab8MwM9d-3UMlN6LKCr95eQ3x-ENIkX889BI9FRH5YIzWQ3mwam8lw8GDshfJajxRmps8aF3ZNOIcEFBTD7dVaGVNcrtl9aCWTx1RNHbn-oP1D67xDxQvw10YSYHKXCCEMBXJCfEi5pPNYCAkPM2bHmdTgKr54qXb0aX_DSr18nQsqVtLpdhjdwejKQ2p2nkUxpn-DfLYdFWHdzFDnUTmi1i6QZ9eu3WyJ6ITJk6bcCYv1yvX2n0tulJh-7oORyBeKDefVi43_VBGWvCEhe1nNBHP038iVwIeBhRCLFdChGSwE1SOQF2T-3p1IjplrZL13DCzM_0-PZXzsvJU61k_-hUe_yEKJCb6MtgDTdNVIFv3sK43fh9yFB-NutjTv2MrkXoWRTKWyNvG0UhG1h76kK3BpR9YmhGT8Tt14OgQjyUdLdq3tyf3MmR-kxkMRh0qVYyi1CDJokTm3oRyNV_vRaj4caNM0FuhVYGCNqfwufyZY7eIER6x5dGF-c6cLiKg-zO6hkqNqzhKdTXFCLqjuaamPO8JZTWa1Qnz_7UcwYE7h1YBL5IF8LfPFFeUAv_AGjnBqxwMbMbqlcPn0tMZAppbI2jHJIm3C7WiCq0c-9pNxfnEuKN6DU9rJbP3g0xaZmSYNscDRoQF4gHthu-qcSOrqZJ0VdIletWB6RnApBNJA9yx2N1T-PxCeSo6vweQhgAYZMU4rkEAY-KI-jAC3rfx7iE4rGCwBTekCBY-ZJUiCaVU7S7wuq-nR0PswClXkcEOlkHsxXbsJJUq7SKnhIycutoSKi97OsOHE1uJHGjws6p0oyP4Y-KXJIG_wnR2DRpdaGapsa71L93gaKIfntGahpFdDt2dj0rS8tdBG5DvRsuwA4UepvT5xG_MmmO2eT35EaZL8LtMhLR_z5dNFHHhYun4KUJKcvpGycQAZKiIEnS8dGUQlNahXbdReQuOwH4o_lkwO0kbpR5spLhPj_W0VzZ4o0Ex7r7q_h9gzXEe9-kGN8Z17fTnmw73hNoUcu1MVYzVvkefhBoBDr9Tm3RCw24ViaP6GyWjCqaGZtwAM5dSR2haSEurchndLHSGAGs04LsdMhlMoMXcsA5U2L64jZrksVTsZ7DXzx_MiEJHA2IrzAL8NkvVEOoNPjMA6rcHtmurhD1dC6rnYWzLCALOiyclXX3qjJicOTLiGH0dEpKsuNGA9GZcGmfLSxjOGppArtVsr7N2kTS5bxS9StAyqx7aoLQhMg2DxNi6PcYOnFhep5FxmshoKTQDU80JA7gqCAmwAlUfjX3k3O9t9VmyTXWNNRUM_rVj-GqUTBqkTpHmWkF0cwxurjoXnDWjPhFnrstj5y_gdntBAHZWLpJw9ImUniFNWO2LgGVgGdngf_BpPse3SU1-pR8HSc2pnBQjlTGrEveikPo_PCH170o6U6vVqqVUyC4ylY7Sbj2sSZHnfoDcS-ViFniWz3fv60vxIla5Iu2lMBTRCIPHGmt7F3tM_BAalqIQIAjDqZ6gjcZqhQiWtZxbtjFfYBeaewtCKwE89hyrhBaX1SewoVLqqnT1TBZ1Lcs711iMdM9tNIQvT-TRbA7C4OBUczlC2nBn5ofhasPlUdD3DpX-RgyT3zMFMLexfey9t--ZYemcit8qe0C5t0p6_Y9KPizdFddewKawlNt5kzmxCef8SNFTZRoDcidubcJwdyRfbt9TIp6C3rEZaDLbPG9c-uVhJK4r0KJ7BrwDuEZK4Ziv4xKrSHb0qZ93Z42OjNzYhbWyKeYJFSgg=="}}
    # {"timestamp":"2025-12-10T05:10:44.324Z","type":"response_item","payload":{"type":"function_call","name":"shell_command","arguments":"{\"command\":\"bash -lc \\\"uname -a; echo '\\\\nUptime:'; uptime; echo '\\\\nDisk usage:'; df -h /; echo '\\\\nMemory (vm_stat):'; vm_stat\\\"\",\"workdir\":\"/Users/a1234/Desktop/GithubProjects/AnyCode-Py\"}","call_id":"call_mNWDDNfZJ1A50Kj8djVX7en3"}}
    # {"timestamp":"2025-12-10T05:10:44.324Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_mNWDDNfZJ1A50Kj8djVX7en3","output":"Exit code: 0\nWall time: 0.1 seconds\nOutput:\n/opt/homebrew/Library/Homebrew/cmd/shellenv.sh: line 18: /bin/ps: Operation not permitted\nDarwin HUAWEI-MateBook-Pro.local 24.6.0 Darwin Kernel Version 24.6.0: Mon Aug 11 21:16:21 PDT 2025; root:xnu-11417.140.69.701.11~1/RELEASE_ARM64_T6000 arm64\n\\nUptime:\n13:10  2 users, load averages: 11.32 9.11 8.93\n\\nDisk usage:\nFilesystem        Size    Used   Avail Capacity iused ifree %iused  Mounted on\n/dev/disk3s1s1   926Gi    10Gi   500Gi     3%    426k  4.3G    0%   /\n\\nMemory (vm_stat):\nMach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free:                               20194.\nPages active:                            185588.\nPages inactive:                          183744.\nPages speculative:                          907.\nPages throttled:                              0.\nPages wired down:                        188415.\nPages purgeable:                            650.\n\"Translation faults\":                3162193103.\nPages copy-on-write:                  114376940.\nPages zero filled:                    915653288.\nPages reactivated:                    958294683.\nPages purged:                         124463928.\nFile-backed pages:                       124235.\nAnonymous pages:                         246004.\nPages stored in compressor:             1857192.\nPages occupied by compressor:            415693.\nDecompressions:                      1091405179.\nCompressions:                        1192273819.\nPageins:                               95903345.\nPageouts:                               2073937.\nSwapins:                               15647475.\nSwapouts:                              18341992.\n"}}
    # {"timestamp":"2025-12-10T05:10:44.324Z","type":"turn_context","payload":{"cwd":"/Users/a1234/Desktop/GithubProjects/AnyCode-Py","approval_policy":"never","sandbox_policy":{"type":"workspace-write","network_access":false,"exclude_tmpdir_env_var":false,"exclude_slash_tmp":false},"model":"gpt-5.1-codex-max","effort":"xhigh","summary":"auto"}}
    # {"timestamp":"2025-12-10T05:10:44.551Z","type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":3110,"cached_input_tokens":2048,"output_tokens":334,"reasoning_output_tokens":256,"total_tokens":3444},"last_token_usage":{"input_tokens":3110,"cached_input_tokens":2048,"output_tokens":334,"reasoning_output_tokens":256,"total_tokens":3444},"model_context_window":258400},"rate_limits":{"primary":null,"secondary":null,"credits":null}}}
    # {"timestamp":"2025-12-10T05:11:17.684Z","type":"event_msg","payload":{"type":"agent_reasoning","text":"**系统概况**\n\n- OS: Darwin 24.6.0 (arm64)  \n- 负载: 运行时间13:10，2用户，负载较高，11.32 9.11 8.93  \n- 磁盘: 根分区926Gi，总用10Gi (3%)，可用约500Gi  \n- 内存: vm_stat显示空闲约2万页 (320MB)，活动约18.5万页 (3GB)，非活动约18.4万页 (3GB)，有线约18.8万页 (3GB)，压缩页约186万 (30GB，表示较重压缩使用)  \n- 其他: Homebrew shellenv尝试调用/bin/ps时因权限受限出现“Operation not permitted”警告，但不影响信息采集  \n\n如需更详细的进程或资源占用分析，可以让我运行top -l 1或其他命令辅助查看。"}}

    def _simple_format(self, session_data: List[Dict]) -> List[Dict]:
        filtered_data = []
        for data in session_data:
            payload = data.get("payload", {})
            role = payload.get("role", "")
            content = payload.get("content", "")
            if role:
                # if role == "user":
                # logger.debug(f"content:\n{content}")
                content = _extract_text_from_message(content)
                # logger.debug(f"content:\n{content}")
                filtered_data.append({"role": role, "content": str(content)})
        return filtered_data

    def load_chat_history(self, session_id: str) -> Optional[List[Dict]]:
        return self._simple_format(self.load_session(session_id=session_id))

    def get_session_list(self, start: int = 0, end: Optional[int] = None) -> List[Dict]:
        end = end or len(self.session_jsonl_path)
        selected_paths = self.session_jsonl_path[start:end]
        result = []

        for path in selected_paths:
            session_id = self.session_id_map[path]
            short_title = self.load_chat_history(session_id)[-1]["content"]

            try:
                short_title = _extract_text_from_message(short_title)
            except Exception as e:
                logger.error(f"Failed to parse content: {e}")
            # list_short_title = list(short_title)
            # logger.debug(short_title)
            # logger.debug(f"type of list_short_title:{type(short_title)}")
            if len(short_title) >= 30:
                short_title = short_title[:27] + "..."
            result.append(
                {
                    "session_id": session_id,
                    "path": str(path),
                    "title": short_title,
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
