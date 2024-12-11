import re
from warnings import warn

import feedparser

from mb_script_convert.transcript import Transcript


def scrape_episode_metadata(transcript: Transcript, url_file_stream_or_string):
    feed = feedparser.parse(url_file_stream_or_string)
    ep_title = transcript.metadata.episode_title
    assert (
        ep_title is not None
    ), "Cannot scrape episode metadata when episode title is not set"
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


def _match_episode(ep_title: str, feed):
    title_re = re.compile(re.escape(ep_title), re.I)
    entry = None
    for entry in feed.entries:
        if title_re.search(entry.title):
            break
    return entry
