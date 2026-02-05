import os
import json
from datetime import datetime
from typing import Dict, Any

from .config import Settings


class StateStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        os.makedirs(self.settings.state_dir, exist_ok=True)

    def _path(self, run_id: str) -> str:
        return os.path.join(self.settings.state_dir, f"{run_id}.json")

    def create(self) -> str:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {"run_id": run_id, "created_at": datetime.now().isoformat(), "steps": []}
        self.save(run_id, data)
        return run_id

    def save(self, run_id: str, data: Dict[str, Any]) -> None:
        with open(self._path(run_id), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, run_id: str) -> Dict[str, Any]:
        with open(self._path(run_id), "r", encoding="utf-8") as f:
            return json.load(f)

    def exists(self, run_id: str) -> bool:
        return os.path.exists(self._path(run_id))
