import atexit
import pickle
from os import environ
from pathlib import Path
from typing import Any


class Cache[_KT, _VT](dict[_KT, _VT]):
    def __init__(self, *args, **kwargs):
        self.modified: bool = False
        return super().__init__(*args, **kwargs)

    def __setitem__(self, key: _KT, value: _VT, /) -> None:
        self.modified = True
        return super().__setitem__(key, value)


XDG_CACHE_HOME = Path(environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
CACHE_FILE = XDG_CACHE_HOME / "mb-scripts" / "cache.pickle"


if CACHE_FILE.exists():
    with CACHE_FILE.open("rb") as f:
        cache: Cache[str, Any] = pickle.load(f)
        cache.modified = False
else:
    cache = Cache()


def save_cache():
    if cache.modified:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("wb") as f:
            pickle.dump(cache, f, pickle.HIGHEST_PROTOCOL)


atexit.register(save_cache)
