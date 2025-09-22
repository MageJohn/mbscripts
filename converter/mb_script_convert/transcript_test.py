import tomllib

from .transcript import Metadata

FRONTMATTER = """
title = "Chapter 1: The Transdimensional Haboob"
date = "2020-10-27T18:01:00"

[params]
series = "Midnight Burger"
season = "1"
season_episode_number = "1"
cover_url = "https://example.com/image.jpg"
"""


class TestMetadataFromFrontmatter:
    def test_from_toml(self, snapshot):
        frontmatter = tomllib.loads(FRONTMATTER)
        metadata = Metadata.from_hugo_frontmatter(frontmatter)

        assert metadata == snapshot

    def test_no_params(self, snapshot):
        frontmatter = {
            "title": "Chapter 42",
        }
        metadata = Metadata.from_hugo_frontmatter(frontmatter)
        assert metadata == Metadata(episode_title="Chapter 42")
