import logging

from .transcript import Transcript

logger = logging.getLogger(__name__)


def _parse_parenthetical(text: str):
    if text[0] != "(":
        return (None, text)
    par_depth = 0
    i = 0
    for i, c in enumerate(text):
        if c == "(":
            par_depth += 1
        elif c == ")":
            par_depth -= 1
        if par_depth == 0:
            break

    if par_depth > 0:
        return (text[: i + 1], None)
    return (text[: i + 1], text[i + 1 :].strip())


def extract_parentheticals(transcript: Transcript):
    i = 0
    while i < len(transcript.content):
        tag, text = transcript.content[i]
        if tag == "dialogue":
            parenthetical, rest = _parse_parenthetical(text)
            if rest is None:
                assert i < len(transcript.content) - 1
                next_tag, next_text = transcript.content[i + 1]
                assert next_tag == "dialogue"
                transcript.content[i] = ("dialogue", f"{parenthetical} {next_text}")
                del transcript.content[i + 1]
                continue  # continue without incrementing i
            elif parenthetical:
                transcript.content[i] = ("parenthetical", parenthetical)
                if len(rest) > 0:
                    transcript.content.insert(i + 1, ("dialogue", rest))
        i += 1


def combine_more(transcript: Transcript):
    for i, (tag, text) in enumerate(transcript.content):
        if tag == "direction" and "(MORE)" in text:
            assert i < len(transcript.content) - 1
            _, contd = transcript.content[i + 1]
            if "(CONT'D)" not in contd.replace("’", "'"):
                logger.warning(
                    f"(CONT'D) not found after (MORE). Instead found {contd}"
                )
            else:
                del transcript.content[i : i + 2]
