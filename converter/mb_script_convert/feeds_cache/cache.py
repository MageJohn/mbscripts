import pickle
from collections import UserDict
from pathlib import Path
from typing import Any


class Cache(UserDict[str, Any]):
    def __init__(self, cache_file: str | Path):
        self.modified: bool = False
        self.cache_file = Path(cache_file)
        super().__init__()

    def __setitem__(self, key: str, value: Any):
        self.modified = True
        self.data[key] = value

    def load_cache(self):
        if self.cache_file.exists():
            with self.cache_file.open("rb") as f:
                cache: Cache = pickle.load(f)
                self.data.update(cache)

    def save_cache(self):
        if self.modified:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with self.cache_file.open("wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
