from __future__ import annotations

import re
from math import isclose
from typing import TYPE_CHECKING

from py_pdf_parser.common import BoundingBox

if TYPE_CHECKING:
    from collections.abc import Callable

    from py_pdf_parser.filtering import PDFElement

PAGE_X_CENTER = 500
PAGE_Y_CENTER = 740


def is_centered(element: PDFElement) -> bool:
    page = element.document.get_page(element.page_number)
    page_middle = page.width / 2

    bbox = element.bounding_box
    el_middle = (bbox.x0 + bbox.x1) / 2

    return isclose(page_middle, el_middle, rel_tol=0.015)


def is_in_top_right(element: PDFElement) -> bool:
    """If it is the top right of the page, could be a page number."""
    bb = element.bounding_box
    return bb.x0 >= PAGE_X_CENTER and bb.y0 >= PAGE_Y_CENTER


def is_off_page(element: PDFElement) -> bool:
    page = element.document.get_page(element.page_number)
    page_bb = BoundingBox(0, page.width, 0, page.height)
    return not element.partially_within(page_bb)


def by_indent(indent: float | int) -> Callable[[PDFElement], bool]:
    def predicate(element: PDFElement) -> bool:
        return isclose(element.bounding_box.x0, indent, abs_tol=10)

    return predicate


def by_min_indent(indent: float | int) -> Callable[[PDFElement], bool]:
    def predicate(element: PDFElement) -> bool:
        return element.bounding_box.x0 > indent

    return predicate


def clean_text(element: PDFElement) -> str:
    return join_lines(element.text())


LINE_BREAK = re.compile(r" *\n *")
HYPHEN_LINE_BREAK = re.compile(r"-\n")


def join_lines(string: str) -> str:
    joined_hyphens = HYPHEN_LINE_BREAK.sub("-", string)
    return LINE_BREAK.sub(" ", joined_hyphens)


class NotTaggedError(Exception):
    pass
