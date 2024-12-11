import argparse
import sys

from mb_script_convert.scrape_rss import scrape_episode_metadata

from .hugo_html import dump
from .import_midnight_burger import import_transcript

MB_RSS_URL = "https://feeds.megaphone.fm/midnightburger"

parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("-o", "--outfile", default=sys.stdout.buffer)
parser.add_argument(
    "--episode-title", help="Override the episode title as parsed from the PDF"
)
parser.add_argument(
    "--skip-scraping",
    action="store_true",
    help="Skip scraping extra metadata from the RSS feed",
)
parser.add_argument(
    "--rss-url",
    default=MB_RSS_URL,
    help="Override the URL of the Midnight Burger RSS feed",
)


def main(infile, outfile, episode_title, skip_scraping, rss_url):
    doc = import_transcript(infile)
    if episode_title:
        doc.metadata.episode_title = episode_title
    if not skip_scraping:
        scrape_episode_metadata(doc, rss_url)
    dump(doc, outfile)


if __name__ == "__main__":
    args = parser.parse_args()
    main(
        args.infile, args.outfile, args.episode_title, args.skip_scraping, args.rss_url
    )
