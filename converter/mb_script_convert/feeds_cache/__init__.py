import atexit
from os import environ
from pathlib import Path

from .cache import Cache

XDG_CACHE_HOME = Path(environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
CACHE_FILE = XDG_CACHE_HOME / "mb-scripts" / "cache.pickle"

cache = Cache(CACHE_FILE)
cache.load_cache()
atexit.register(cache.save_cache)
