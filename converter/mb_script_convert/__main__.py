import argparse
import logging
import sys

from .main import main

logger = logging.getLogger(__name__)

MB_RSS_URL = "https://rss.art19.com/midnight-burger"

parser = argparse.ArgumentParser()
parser.add_argument("IN")
parser.add_argument("-o", "--output", default=sys.stdout.buffer)
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
parser.add_argument(
    "-O", "--overwrite", action="store_true", help="Allow overwriting the output"
)
parser.add_argument("--debug", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()
    try:
        main(
            args.IN,
            args.output,
            args.episode_title,
            args.skip_scraping,
            args.rss_url,
            args.overwrite,
            args.debug,
        )
    except RuntimeError as e:
        logger.error(*e.args)
