import pickle
import re
from os import environ
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from warnings import warn

import feedparser

from mb_script_convert.transcript import Transcript


def scrape_episode_metadata(transcript: Transcript, url_file_stream_or_string):
    ep_title = transcript.metadata.episode_title
    assert (
        ep_title is not None
    ), "Cannot scrape episode metadata when episode title is not set"

    feed = _get_feed(url_file_stream_or_string)
    if feed is None:
        return

    episode = _match_episode(ep_title, feed)
    if episode is None:
        warn(
            f"Could not find episode with title {ep_title} in the RSS feed. Additional metadata has not been scraped"
        )
        return

    m = transcript.metadata
    m.cover_url = episode.image.href
    m.date_published = episode.published
    m.season = episode.itunes_season
    m.season_episode_number = episode.itunes_episode


XDG_CACHE_HOME = Path(environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
CACHE_FILE = XDG_CACHE_HOME / "mb-scripts" / "feeds.pickle"


def _get_feed(url_file_stream_or_string):
    looks_like_url = isinstance(url_file_stream_or_string, str) and urlparse(
        url_file_stream_or_string
    )[0] in ("http", "https")
    if not looks_like_url:
        return feedparser.parse(url_file_stream_or_string)
    url: str = url_file_stream_or_string

    if CACHE_FILE.exists():
        with CACHE_FILE.open("rb") as f:
            feeds: dict[str, Any] = pickle.load(f)
    else:
        feeds = {}

    modified = False
    if url not in feeds:
        feeds[url] = feedparser.parse(url)
        modified = True
        match feeds[url].status:
            case 200 | 302:
                # all good
                pass
            case 301:
                warn(
                    f"HTTP response 301: {url} has permanently moved to {feeds[url].href}"
                )
            case _:
                warn(
                    f"Something went wrong fetching {url} (status {feeds[url].status}). Cannot scrape metadata"
                )
                return
    else:
        old_feed = feeds[url]
        new_feed = feedparser.parse(
            url, etag=old_feed.get("etag"), modified=old_feed.get("modified")
        )
        match new_feed.status:
            case 200 | 302:
                feeds[url] = new_feed
                modified = True
            case 304:
                # the feed has not been modified
                pass
            case 301:
                warn(
                    f"HTTP response 301: {url} has permanently moved to {new_feed.href}"
                )
                feeds[url] = new_feed
                modified = True
            case _:
                warn(
                    f"Something went wrong fetching {url} (status {new_feed.status}). Using cached feed."
                )

    if modified:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with CACHE_FILE.open("wb") as f:
            pickle.dump(feeds, f, pickle.HIGHEST_PROTOCOL)

    return feeds[url]


def _match_episode(ep_title: str, feed):
    title_re = re.compile(re.escape(ep_title), re.I)
    entry = None
    for entry in feed.entries:
        if title_re.search(entry.title):
            break
    return entry
