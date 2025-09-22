import logging
from collections.abc import Sequence
from dataclasses import fields
from datetime import datetime
from time import mktime
from urllib.parse import urlparse

import feedparser
from adaptix import P, Retort, loader, name_mapping
from feedparser import FeedParserDict
from rapidfuzz import fuzz

from .feeds_cache import cache
from .transcript import Metadata, Transcript

logger = logging.getLogger(__name__)

retort = Retort(
    recipe=[
        name_mapping(
            Metadata,
            map=[
                ("date_published", "published_parsed"),
                ("season", "itunes_season"),
                ("episode", "itunes_episode"),
                ("season_episode_number", "itunes_episode"),
                ("cover_url", "image"),
            ],
        ),
        loader(
            P[Metadata].date_published, lambda st: datetime.fromtimestamp(mktime(st))
        ),
    ],
    strict_coercion=False,
)


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

    m = retort.load(episode, Metadata)

    transcript.metadata.merge(m)

    for field in fields(transcript.metadata):
        name, value = field.name, getattr(transcript.metadata, field.name)
        if value is None:
            logger.warning("Could not find a value for %s", name)


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
                    "HTTP response 301: %s has permanently moved to %s",
                    url,
                    cache[url].href,
                )
            case _:
                logger.warning(
                    "Something went wrong fetching %s (status %s). Cannot scrape metadata",
                    url,
                    cache[url].status,
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
                    "HTTP response 301: %s has permanently moved to %s",
                    url,
                    new_feed.href,
                )
                cache[url] = new_feed
            case _:
                logger.warning(
                    "Something went wrong fetching %s (status %s). Using cached feed.",
                    url,
                    new_feed.status,
                )

    return cache[url]


SIMILARITY_THRESHOLD = 85


def _match_episode(ep_title: str, feed: FeedParserDict) -> FeedParserDict | None:
    most_similar = (0, None)
    matches: list[FeedParserDict] = []
    for entry in feed.entries:
        # partial ratio
        ratio = fuzz.partial_ratio(ep_title, entry.title)
        if ratio > most_similar[0]:
            most_similar = (ratio, entry)
        if ratio > SIMILARITY_THRESHOLD:
            matches.append(entry)
    assert most_similar[1] is not None
    if len(matches) > 0:
        if len(matches) == 1:
            result = matches[0]
        else:
            ratios = [fuzz.ratio(ep_title, e.title) for e in matches]
            result = matches[_argmax(ratios)]
        logger.info("Matched episode '%s' in RSS feed", result.title)
        return result
    else:
        logger.warning("Could not find entry matching '%s'", ep_title)
        logger.warning(
            "The most similar title is %s (similarity %s)",
            most_similar[1].title,
            most_similar[0],
        )
        logger.warning("Set the correct title with the --episode-title flag")


def _argmax(a: Sequence[float]):
    """Return the index of the maximum value in a."""
    return max(range(len(a)), key=lambda x: a[x])
