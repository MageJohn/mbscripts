import logging
from pathlib import Path

from mb_script_convert.scrape_rss import scrape_episode_metadata

from . import normalisations
from .hugo_html import dump, load_metadata
from .import_midnight_burger import import_transcript

logger = logging.getLogger(__name__)


def main(
    in_file_or_dir: str,
    out_file_or_dir: str,
    episode_title: str | None,
    skip_scraping: bool,
    rss_url: str | None,
    overwrite: bool,
    debug: bool,
):
    logging.basicConfig(level=logging.INFO, format="{levelname}: {message}", style="{")

    in_path = Path(in_file_or_dir)
    out_path = Path(out_file_or_dir)

    if in_path.is_dir():
        if not out_path.is_dir():
            raise RuntimeError(
                "when input is a directory, output must also be a directory"
            )
        for pdf_path in in_path.glob("**/*.pdf"):
            output_file_path = make_output_path(pdf_path, in_path, out_path)
            if not overwrite and output_file_path.exists():
                logger.info(f"Skipping: {pdf_path} -> {output_file_path}")
                continue
            convert_transcript(
                pdf_path,
                output_file_path,
                episode_title,
                skip_scraping,
                rss_url,
                debug,
            )
    elif in_path.is_file():
        if not overwrite and out_path.exists():
            logger.info(f"Skipping: {in_path} -> {out_path}")
        else:
            convert_transcript(
                in_path, out_path, episode_title, skip_scraping, rss_url, debug
            )
    else:
        raise RuntimeError(f"not a valid file or directory: {in_file_or_dir}")


def make_output_path(input: Path, input_base: Path, output_base: Path) -> Path:
    """Make an output path for a converted PDF

    Will recreate the relative path from `input_base` to `input` in
    `output_base`, with `.html` replacing `.pdf`. However, if
    `name/index.html` exists in the output_base path, then return that
    `index.html` file to ensure proper overwriting behaviour.
    Arguments:
    input -- path to input PDF file; must be a subpath of `input_base`
    input_base -- parent path of `input`; the path below this will be recreated in `output_path`
    output_base -- the target directory where the output path will be
    """
    rel_input = input.relative_to(input_base)
    output_html = output_base / rel_input.with_suffix(".html")
    output_indexhtml = output_base / rel_input.with_name(input.stem) / "index.html"

    if output_indexhtml.exists():
        return output_indexhtml
    else:
        return output_html


def convert_transcript(
    input: Path,
    output: Path,
    episode_title: str | None,
    skip_scraping: bool,
    rss_url: str | None,
    debug: bool,
):
    logger.info(f"Converting: {input} -> {output}")
    doc = import_transcript(str(input), debug)
    normalisations.run_all(doc)
    if output.exists():
        load_metadata(output, doc)
    if episode_title:
        doc.metadata.episode_title = episode_title
    if not skip_scraping:
        scrape_episode_metadata(doc, rss_url)
    dump(doc, output)
