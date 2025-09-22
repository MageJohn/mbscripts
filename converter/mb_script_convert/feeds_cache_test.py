from pathlib import Path

from .feeds_cache import Cache


def test_cache(tmp_path: Path):
    test_cache_file = tmp_path / "cache.pickle"
    test_cache = Cache(test_cache_file)

    assert not test_cache_file.exists()
    test_cache.save_cache()
    assert not test_cache_file.exists()
    test_cache["foo"] = "bar"
    test_cache.save_cache()
    assert test_cache_file.exists()

    test_cache_2 = Cache(test_cache_file)
    test_cache_2.load_cache()
    assert test_cache_2.modified is False
    assert test_cache_2["foo"] == "bar"
