from __future__ import annotations
import json
from pathlib import Path
def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open() as f: return [json.loads(line) for line in f if line.strip()]
