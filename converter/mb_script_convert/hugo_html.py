import logging
import tomllib
from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from typing import IO, Union

import lxml.html.builder as b
import tomli_w
from adaptix import P, Retort, as_sentinel, name_mapping
from lxml import html

from .transcript import Metadata, Transcript

logger = logging.getLogger(__name__)


retort = Retort(
    recipe=[
        name_mapping(
            Metadata,
            map=[
                ("episode_title", "title"),
                ("date_published", "date"),
                (".*", ["params", ...]),
            ],
            omit_default=True,
        ),
        as_sentinel(P[Metadata][Union][None]),
    ],
    strict_coercion=False,
)


def dump(transcript: Transcript, file_or_path: str | Path | IO[bytes]):
    if isinstance(file_or_path, (str, Path)):
        path = Path(file_or_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        file = path.open("wb+")
    else:
        file = nullcontext(file_or_path)
    with file as fh:
        fh.write(b"+++\n")
        tomli_w.dump(retort.dump(transcript.metadata), fh)
        fh.write(b"+++\n\n")

        for el in transcript.content:
            html_el = b.P(b.CLASS(el[0]), el[1])
            html_el_str = html.tostring(html_el, pretty_print=True, encoding="utf-8")
            assert isinstance(html_el_str, bytes)  # for type hinting
            fh.write(html_el_str)


def dumps(transcript: Transcript) -> str:
    out = BytesIO()
    dump(transcript, out)
    return out.getvalue().decode("utf-8")


def load_metadata(file_or_path: str | Path | IO[str], transcript: Transcript):
    if isinstance(file_or_path, (str, Path)):
        path = Path(file_or_path)
        assert path.exists(), "Invalid path passed"
        file = path.open("r", encoding="utf-8")
    else:
        file = nullcontext(file_or_path)
    with file as fh:
        if fh.readline() != "+++\n":
            logger.warning("Existing output file is not a valid Hugo document")
        frontmatter_str = ""
        while (line := fh.readline()) != "+++\n":
            frontmatter_str += line

    frontmatter = tomllib.loads(frontmatter_str)
    transcript.metadata = retort.load(frontmatter, Metadata)
