"""
Functions which normalise the text content of a Transcript
"""

from mb_script_convert.transcript import Transcript


def run_all(transcript: Transcript):
    title_period(transcript)


def title_period(transcript: Transcript):
    title = transcript.metadata.episode_title
    if title and title[-1] == ".":
        transcript.metadata.episode_title = title[:-1]
