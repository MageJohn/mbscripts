"""Functions which normalise the text content of a Transcript."""

from mb_script_convert.transcript import Transcript


def run_all(transcript: Transcript):
    title_period(transcript)
    series_colon(transcript)


def title_period(transcript: Transcript):
    title = transcript.metadata.episode_title
    if title and title[-1] == ".":
        transcript.metadata.episode_title = title[:-1]


def series_colon(transcript: Transcript):
    series = transcript.metadata.series
    if series and series[-1] == ":":
        transcript.metadata.series = series[:-1]
