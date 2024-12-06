from py_pdf_parser.loaders import load_file
from py_pdf_parser.exceptions import NoElementFoundError, ElementOutOfRangeError
from py_pdf_parser.common import BoundingBox

import importlib
import argparse
from math import isclose
from sys import stderr
import re
import html
from textwrap import dedent
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('-V', '--visualise', action='store_true')


DIRECTIONS_INDENT = 108.0
DIALOGUE_INDENT = 144.0


def main(infile, vis):
    doc = parse_file(infile)
    if vis:
        visualise(doc, show_info=True)
    print(render(doc))


def parse_file(infile):
    doc = load_file(infile)

    # Ignore elements off of the page
    doc.elements.filter(is_off_page).ignore_elements()

    # Ignore page numbers
    page_numbers = doc.elements.filter_by_regex(r'\d+\.').filter(is_in_top_right)
    if len(page_numbers) == 0:
        log("Warning: could not find page numbers.")
    page_numbers.ignore_elements()

    # Detect and ignore title page
    first_page = doc.get_page(1).elements
    if all(is_centered(el) for el in first_page) and len(first_page) <= 5:
        first_page.ignore_elements()
        first_page = doc.elements.filter_by_page(2)
    else:
        log("Warning: could not find title page")

    # Tag front matter
    first_page[0].add_tag('series_title')
    first_page[1].add_tag('episode_title')

    # Tag ending
    last_page = doc.pages[-1].elements
    try:
        end = last_page.filter_by_regex(r'.*end.*', re.I).last()
        end.add_tag('end')
    except NoElementFoundError:
        log("Warning: could not find THE END or equivalent")

    # Rest of the script
    script = doc.elements - doc.elements.filter_by_tags('series_title', 'episode_title', 'end')

    directions = script.filter(by_indent(DIRECTIONS_INDENT))
    dialogue = script.filter(by_indent(DIALOGUE_INDENT))

    directions.add_tag_to_elements('direction/character')
    dialogue.add_tag_to_elements('dialogue')

    others = script - script.filter_by_tags('direction/character', 'dialogue')
    if len(others) > 0:
        log("Warning: found text that has not been categorised:")
        for el in others:
            log(el.text(), el.bounding_box)

    script = directions | dialogue

    for el in directions:
        try:
            next = script.move_forwards_from(el)
        except ElementOutOfRangeError:
            next = None
        if next is not None and 'dialogue' in next.tags:
            el.add_tag('character')
        else:
            el.add_tag('direction')

    for el in directions.filter_by_text_contains('(MORE)'):
        contd = directions.move_forwards_from(el)
        if "(CONT'D)" not in contd.text().replace('’', "'"):
            log(f"Warning: Page {el.page_number}: (CONT'D) not found after (MORE). Instead found {contd.text()}")
        else:
            el.ignore()
            contd.ignore()

    return doc

def render(tagged_doc):
    series_title = clean_text(tagged_doc.elements.filter_by_tag('series_title').extract_single_element())
    episode_title = clean_text(tagged_doc.elements.filter_by_tag('episode_title').extract_single_element())
    content = "\n".join(s for s in (render_element(el) for el in tagged_doc.elements) if s is not None)
    header = dedent(f"""
        +++
        date = '{datetime.today().strftime('%Y-%m-%d')}'
        draft = true
        title = '{series_title} - {episode_title}'
        +++
    """).strip()

    return "\n".join([header, "", content])


def render_element(element):
    if 'series_title' in element.tags:
        pass
    elif 'episode_title' in element.tags:
        pass
    elif 'end' in element.tags:
        return f'<p class="end">{clean_text(element)}</p>'
    elif 'direction' in element.tags:
        return f'<p class="direction">{clean_text(element)}</p>'
    elif 'character' in element.tags:
        return f'<p class="character">{clean_text(element)}</p>'
    elif 'dialogue' in element.tags:
        return f'<p class="dialogue">{clean_text(element)}</p>'
    else:
        raise NotTaggedError(f'Element is not properly tagged: {element}')


def clean_text(element):
    return html.escape(join_lines(element.text()))


def is_centered(element):
    page = element.document.get_page(element.page_number)
    page_middle = page.width / 2

    bbox = element.bounding_box
    el_middle = (bbox.x0 + bbox.x1) / 2

    return isclose(page_middle, el_middle, rel_tol=0.015)


def is_in_top_right(element):
    """
        If it is the top right of the page, could be a page number
    """
    bb = element.bounding_box
    return bb.x0 >= 500 and bb.y0 >= 740


def is_off_page(element):
    page = element.document.get_page(element.page_number)
    page_bb = BoundingBox(0, page.width, 0, page.height)
    return not element.partially_within(page_bb)


def by_indent(indent):
    def filter(element):
        return isclose(element.bounding_box.x0, indent, abs_tol=10)
    return filter


LINE_BREAK = re.compile(r' *\n *')
def join_lines(str):
    return LINE_BREAK.sub(' ', str)


def log(*args):
    print(*args, file=stderr)


def visualise(document, **kwargs):
    """
        It seems importing this module is very slow, so do it lazily
    """
    from py_pdf_parser.visualise import visualise
    visualise(document, **kwargs)


class NotTaggedError(Exception):
    pass


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.infile, args.visualise)
