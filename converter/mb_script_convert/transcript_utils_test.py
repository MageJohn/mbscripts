import pytest

from .transcript import Transcript
from .transcript_utils import _parse_parenthetical, combine_more, extract_parentheticals


def test__parse_parenthetical():
    assert _parse_parenthetical("(foo) bar") == ("(foo)", "bar")
    assert _parse_parenthetical("(foo (bar)) baz") == ("(foo (bar))", "baz")
    assert _parse_parenthetical("foo") == (None, "foo")
    assert _parse_parenthetical("(foo") == ("(foo", None)


@pytest.mark.parametrize(
    "content_in, content_out",
    [
        (
            [
                ("dialogue", "(foo) bar"),
                ("parenthetical", "(foo) bar"),
                ("direction", "(foo) bar"),
                ("character", "(foo) bar"),
                ("end", "(foo) bar"),
            ],
            [
                ("parenthetical", "(foo)"),
                ("dialogue", "bar"),
                ("parenthetical", "(foo) bar"),
                ("direction", "(foo) bar"),
                ("character", "(foo) bar"),
                ("end", "(foo) bar"),
            ],
        ),
        (
            [
                ("dialogue", "(foo"),
                ("dialogue", "bar) foo"),
            ],
            [("parenthetical", "(foo bar)"), ("dialogue", "foo")],
        ),
        (
            [
                ("dialogue", "(foo"),
                ("dialogue", "bar)"),
            ],
            [("parenthetical", "(foo bar)")],
        ),
        ([("dialogue", "(foo)")], [("parenthetical", "(foo)")]),
    ],
)
def test_extract_parentheticals(content_in, content_out):
    transcript = Transcript(content=list(content_in))

    extract_parentheticals(transcript)

    assert transcript.content == content_out


@pytest.mark.parametrize(
    "content_in, content_out",
    [
        ([("direction", "(MORE)"), ("direction", "(CONT'D)")], []),
        ([("direction", "(MORE)"), ("direction", "(CONT’D)")], []),
        ([("direction", "(MORE)"), ("direction", "AVA (CONT'D)")], []),
        (
            [
                ("dialogue", "foo"),
                ("direction", "(MORE)"),
                ("direction", "(CONT'D)"),
                ("dialogue", "bar"),
            ],
            [("dialogue", "foo"), ("dialogue", "bar")],
        ),
        (
            [
                ("dialogue", "foo1"),
                ("direction", "(MORE)"),
                ("direction", "(CONT'D)"),
                ("dialogue", "bar1"),
                ("dialogue", "foo2"),
                ("direction", "(MORE)"),
                ("direction", "(CONT'D)"),
                ("dialogue", "bar2"),
            ],
            [
                ("dialogue", "foo1"),
                ("dialogue", "bar1"),
                ("dialogue", "foo2"),
                ("dialogue", "bar2"),
            ],
        ),
    ],
)
def test_combine_more(content_in, content_out):
    transcript = Transcript(content=list(content_in))
    combine_more(transcript)
    assert transcript.content == content_out
