from pathlib import Path
import orjson
from typing import List, Dict


def load_jsonl(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [orjson.loads(line) for line in f]
