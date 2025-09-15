import pytest

from .transcript import Transcript
from .transcript_utils import (
    _parse_parenthetical,
    combine_more,
    extract_parentheticals,
    split_short_dialogue,
)


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


@pytest.mark.parametrize(
    "content_in, content_out",
    [
        (
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("direction", "CLEMENTINE Yes."),
            ],
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes."),
            ],
        ),
        (
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("direction", "CLEMENTINE (CONT'D) Yes."),
                ("direction", "CLEMENTINE (CONT’D) Yes."),
            ],
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("character", "CLEMENTINE (CONT'D)"),
                ("dialogue", "Yes."),
                ("character", "CLEMENTINE (CONT’D)"),
                ("dialogue", "Yes."),
            ],
        ),
        (
            [
                ("character", "TED BOT"),
                ("dialogue", "Yes, thank you."),
                ("direction", "TED BOT Yes."),
            ],
            [
                ("character", "TED BOT"),
                ("dialogue", "Yes, thank you."),
                ("character", "TED BOT"),
                ("dialogue", "Yes."),
            ],
        ),
        (
            [
                ("character", "TED BOT"),
                ("dialogue", "Yes, thank you."),
                ("direction", "TED BOT (CONT'D) Yes."),
            ],
            [
                ("character", "TED BOT"),
                ("dialogue", "Yes, thank you."),
                ("character", "TED BOT (CONT'D)"),
                ("dialogue", "Yes."),
            ],
        ),
        (
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("direction", "CLEMENTINE WALKS AROUND"),
            ],
            [
                ("character", "CLEMENTINE"),
                ("dialogue", "Yes, thank you."),
                ("direction", "CLEMENTINE WALKS AROUND"),
            ],
        ),
        (
            [
                ("character", "POTION MAESTRO"),
                ("dialogue", "What do you... want?"),
                ("direction", "POTION MAESTRO ... yes."),
            ],
            [
                ("character", "POTION MAESTRO"),
                ("dialogue", "What do you... want?"),
                ("character", "POTION MAESTRO"),
                ("dialogue", "... yes."),
            ],
        ),
    ],
)
def test_split_short_dialogue(content_in, content_out):
    transcript = Transcript(content=list(content_in))

    split_short_dialogue(transcript)

    assert transcript.content == content_out
