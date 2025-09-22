import logging
from collections.abc import Sequence
from dataclasses import fields
from datetime import datetime
from time import struct_time
from typing import TypeVar
from urllib.parse import urlparse

import feedparser
from feedparser import FeedParserDict
from rapidfuzz import fuzz

from .feeds_cache import cache
from .transcript import Metadata, Transcript

logger = logging.getLogger(__name__)


def scrape_episode_metadata(transcript: Transcript, url_file_stream_or_string):
    ep_title = transcript.metadata.episode_title
    assert ep_title is not None, (
        "Cannot scrape episode metadata when episode title is not set"
    )

    feed = _get_feed(url_file_stream_or_string)
    if feed is None:
        return

    episode = _match_episode(ep_title, feed)
    if episode is None:
        return

    m = Metadata()
    published_parsed = _safe_get(episode, struct_time, "published_parsed")
    if published_parsed is not None:
        m.date_published = _date_to_iso(published_parsed)
    m.season = _safe_get(episode, str, "itunes_season")
    m.season_episode_number = _safe_get(episode, str, "itunes_episode")
    m.cover_url = getattr(_safe_get(episode, FeedParserDict, "image"), "href", None)

    transcript.metadata.merge(m)

    for field in fields(transcript.metadata):
        name, value = field.name, getattr(transcript.metadata, field.name)
        if value is None:
            logger.warning(f"Could not find a value for {name}")



T = TypeVar("T")


def _safe_get(feed_dict: FeedParserDict, type_: type[T], key: str) -> T | None:
    """Type-safe get from a FeedParserDict"""
    ret = feed_dict.get(key)
    if isinstance(ret, type_):
        return ret


def _get_feed(url_file_stream_or_string) -> FeedParserDict | None:
    looks_like_url = isinstance(url_file_stream_or_string, str) and urlparse(
        url_file_stream_or_string
    )[0] in ("http", "https")
    if not looks_like_url:
        return feedparser.parse(url_file_stream_or_string)
    url: str = url_file_stream_or_string

    if url not in cache:
        cache[url] = feedparser.parse(url)
        match cache[url].status:
            case 200 | 302:
                # all good
                pass
            case 301:
                logger.warning(
                    f"HTTP response 301: {url} has permanently moved to {cache[url].href}"
                )
            case _:
                logger.warning(
                    f"Something went wrong fetching {url} (status {cache[url].status}). Cannot scrape metadata"
                )
                return
    else:
        cached_feed = cache[url]
        new_feed = feedparser.parse(
            url, etag=cached_feed.get("etag"), modified=cached_feed.get("modified")
        )
        match new_feed.status:
            case 200 | 302:
                cache[url] = new_feed
            case 304:
                # the feed has not been modified
                pass
            case 301:
                logger.warning(
                    f"HTTP response 301: {url} has permanently moved to {new_feed.href}"
                )
                cache[url] = new_feed
            case _:
                logger.warning(
                    f"Something went wrong fetching {url} (status {new_feed.status}). Using cached feed."
                )

    return cache[url]


def _match_episode(ep_title: str, feed: FeedParserDict) -> FeedParserDict | None:
    most_similar = (0, None)
    matches: list[FeedParserDict] = []
    for entry in feed.entries:
        # partial ratio
        ratio = fuzz.partial_ratio(ep_title, entry.title)
        if ratio > most_similar[0]:
            most_similar = (ratio, entry)
        if ratio > 85:
            matches.append(entry)
    assert most_similar[1] is not None
    if len(matches) > 0:
        if len(matches) == 1:
            result = matches[0]
        else:
            ratios = list(map(lambda e: fuzz.ratio(ep_title, e.title), matches))
            result = matches[_argmax(ratios)]
        logger.info(f"Matched episode '{result.title}' in RSS feed")
        return result
    else:
        logger.warning(f"Could not find entry matching '{ep_title}'")
        logger.warning(
            f"The most similar title is {most_similar[1].title} (similarity {most_similar[0]})"
        )
        logger.warning("Set the correct title with the --episode-title flag")


def _argmax(a: Sequence[float]):
    """Return the index of the maximum value in a"""
    return max(range(len(a)), key=lambda x: a[x])


def _date_to_iso(date: struct_time):
    return datetime(
        date.tm_year,
        date.tm_mon,
        date.tm_mday,
        date.tm_hour,
        date.tm_min,
        date.tm_sec,
    ).isoformat()
