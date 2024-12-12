from pathlib import Path

import pytest

from mb_script_convert.hugo_html import dump, dumps
from mb_script_convert.transcript import Metadata, Transcript


@pytest.fixture
def transcript():
    return Transcript(
        metadata=Metadata(
            episode_title="Panopticon", season=4, date_published="October 17, 2019"
        ),
        content=[
            ("direction", "TAPE CLICKS ON"),
            ("character", "PETER"),
            ("parenthetical", "(pleasantly)"),
            ("dialogue", "Is everything alright, Martin?"),
        ],
    )


def test_dumps(transcript, snapshot):
    assert dumps(transcript) == snapshot


def test_dump(transcript, snapshot, tmp_path: Path):
    out_path = tmp_path / "out_Path.html"
    out_str = (tmp_path / "out_str.html").as_posix()
    out_fh_path = tmp_path / "out_fh.html"

    dump(transcript, out_path)
    dump(transcript, out_str)
    with open(out_fh_path, "wb") as out_fh:
        dump(transcript, out_fh)

    with open(out_path, "r") as fh:
        assert fh.read() == snapshot
    with open(out_str, "r") as fh:
        assert fh.read() == snapshot
    with open(out_fh_path, "r") as fh:
        assert fh.read() == snapshot
