from .scrape_rss import _match_episode
from feedparser import FeedParserDict


class TestMatchEpisode:
    ENTRIES = [
        {"title": "Chapter 1: The Transdimensional Haboob"},
        {"title": "Chapter 38: Welcome to the Triad"},
        {"title": "Patreon Drop! Shift Notes Chapter 38: Welcome to the Triad"},
        {"title": "Young Leif Part 1: Bertiluna"},
        {"title": "Welcome to the Horizon Part 1: Relentless Rick"},
        {"title": "Patreon Drop! Shift Notes Welcome to the Horizon Part 1: Relentless Rick"},
    ]

    FAKE_FEED = FeedParserDict({"entries": [FeedParserDict(e) for e in ENTRIES]})

    def test_basic_functionality(self):
        result = _match_episode(
            "Chapter 1: The Transdimensional Haboob", self.FAKE_FEED
        )
        assert result == self.ENTRIES[0]

    def test_excludes_extra_text(self):
        result = _match_episode("Chapter 38: Welcome to the Triad", self.FAKE_FEED)
        assert result == self.ENTRIES[1]

    def test_gets_sub_series(self):
        result1 = _match_episode("Part 1: Bertiluna", self.FAKE_FEED)
        assert result1 == self.ENTRIES[3]

        result2 = _match_episode("Part 1: Relentless Rick", self.FAKE_FEED)
        assert result2 == self.ENTRIES[4]
