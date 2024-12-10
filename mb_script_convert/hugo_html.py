from contextlib import nullcontext
from io import BytesIO
from pathlib import Path
from typing import IO

import lxml.html as html
import lxml.html.builder as b
import tomli_w

from .transcript import Metadata, Transcript

type HugoFrontmatter = dict[str, str | HugoFrontmatter]


def dump(transcript: Transcript, file_or_path: str | Path | IO[bytes]):
    if isinstance(file_or_path, str) or isinstance(file_or_path, Path):
        file = open(file_or_path, "wb+")
    else:
        file = nullcontext(file_or_path)
    with file as fh:
        fh.write(b"+++\n")
        tomli_w.dump(_metadata_to_hugo_frontmatter(transcript.metadata), fh)
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


def _metadata_to_hugo_frontmatter(metadata: Metadata):
    frontmatter: HugoFrontmatter = {"params": {}}
    for k in metadata:
        if k == "episode-title":
            frontmatter["title"] = metadata[k]
        else:
            frontmatter["params"][k] = metadata[k]  # pyright: ignore [reportIndexIssue]
    return frontmatter
