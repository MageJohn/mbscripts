import atexit
import pickle
from os import environ
from pathlib import Path
from typing import Any

XDG_CACHE_HOME = Path(environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
CACHE_FILE = XDG_CACHE_HOME / "mb-scripts" / "cache.pickle"


class Cache(dict[str, Any]):
    def __init__(self, cache_file: str | Path):
        self.modified: bool = False
        self.cache_file = Path(cache_file)
        return super().__init__()

    def __setitem__(self, key: str, value: Any, /) -> None:
        self.modified = True
        return super().__setitem__(key, value)

    def load_cache(self):
        if self.cache_file.exists():
            with self.cache_file.open("rb") as f:
                cache: Cache = pickle.load(f)
                self.update(cache)

    def save_cache(self):
        if self.modified:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with self.cache_file.open("wb") as f:
                pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)


cache = Cache(CACHE_FILE)
cache.load_cache()
atexit.register(cache.save_cache)
