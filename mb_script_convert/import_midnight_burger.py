import re
from warnings import warn

from py_pdf_parser.exceptions import ElementOutOfRangeError, NoElementFoundError
from py_pdf_parser.loaders import PDFDocument, load_file
from titlecase import titlecase

from mb_script_convert.pdf_utils import (
    by_indent,
    by_min_indent,
    clean_text,
    is_centered,
    is_in_top_right,
    is_off_page,
)

from .transcript import Transcript
from .transcript_utils import combine_more, extract_parentheticals

DIRECTIONS_INDENT = 108.0
DIALOGUE_INDENT = 144.0


def import_transcript(pdf_file: str, debug: bool) -> Transcript:
    pdf = load_file(pdf_file)
    tag_pdf(pdf)
    if debug:
        _visualise(pdf)
    transcript = tagged_pdf_to_transcript(pdf)
    extract_parentheticals(transcript)
    combine_more(transcript)
    return transcript


def _visualise(pdf: PDFDocument):
    from py_pdf_parser.visualise import visualise

    visualise(pdf)


def tag_pdf(pdf: PDFDocument):
    # Ignore elements off of the page
    pdf.elements.filter(is_off_page).ignore_elements()

    # Ignore page numbers
    page_numbers = pdf.elements.filter_by_regex(r"\d+\.").filter(is_in_top_right)
    if len(page_numbers) == 0:
        warn("Warning: could not find page numbers.")
    page_numbers.ignore_elements()

    # Detect and ignore title page
    first_page = pdf.get_page(1).elements
    if all(is_centered(el) for el in first_page) and len(first_page) <= 5:
        first_page.ignore_elements()
        first_page = pdf.elements.filter_by_page(2)
    else:
        warn("Warning: could not find title page")

    # Tag front matter
    first_page[0].add_tag("series_title")
    first_page[1].add_tag("episode_title")

    # Tag ending
    last_page = pdf.pages[-1].elements
    try:
        end = (
            last_page.filter_by_regex(r".*\bend\b.*", re.I)
            .filter(by_min_indent(DIALOGUE_INDENT + 10))
            .last()
        )
        end.add_tag("end")
    except NoElementFoundError:
        warn("Warning: could not find THE END or equivalent")

    # Rest of the script
    script = pdf.elements - pdf.elements.filter_by_tags(
        "series_title", "episode_title", "end"
    )

    directions = script.filter(by_indent(DIRECTIONS_INDENT))
    dialogue = script.filter(by_indent(DIALOGUE_INDENT))

    directions.add_tag_to_elements("direction/character")
    dialogue.add_tag_to_elements("dialogue")

    others = script - script.filter_by_tags("direction/character", "dialogue")
    if len(others) > 0:
        print("Warning: found text that has not been categorised:")
        for el in others:
            print(f"{repr(el.text())} {el.bounding_box}")

    script = directions | dialogue

    for el in directions:
        try:
            next = script.move_forwards_from(el)
        except ElementOutOfRangeError:
            next = None
        if next is not None and "dialogue" in next.tags:
            el.tags = set(["character"])
        else:
            el.tags = set(["direction"])


def tagged_pdf_to_transcript(tagged: PDFDocument) -> Transcript:
    transcript = Transcript()
    for el in tagged.elements:
        if "series_title" in el.tags:
            transcript.metadata.series = titlecase(clean_text(el))
        elif "episode_title" in el.tags:
            transcript.metadata.episode_title = clean_text(el)
        elif "direction" in el.tags:
            transcript.add_content("direction", clean_text(el))
        elif "character" in el.tags:
            transcript.add_content("character", clean_text(el))
        elif "dialogue" in el.tags:
            transcript.add_content("dialogue", clean_text(el))
        elif "end" in el.tags:
            transcript.add_content("end", clean_text(el))
    return transcript
