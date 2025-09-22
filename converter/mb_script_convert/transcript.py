import logging
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Literal, Optional, Self

logger = logging.getLogger(__name__)

type Tag = Literal["direction", "character", "parenthetical", "dialogue", "end"]
type Content = list[tuple[Tag, str]]


type HugoFrontmatter = dict[str, str | HugoFrontmatter]


@dataclass
class Metadata:
    episode_title: Optional[str] = None
    series: Optional[str] = None
    season: Optional[int] = None
    season_episode_number: Optional[int] = None
    date_published: Optional[datetime] = None
    cover_url: Optional[str] = None

    def merge(self, other: Self):
        for field in fields(self):
            if getattr(self, field.name) is None:
                setattr(self, field.name, getattr(other, field.name))


class Transcript:
    """
    Represents a transcript in a format agnostic way.
    Used as an intermediate step when converting.
    """

    content: Content
    metadata: Metadata

    def __init__(
        self, metadata: Metadata | None = None, content: Content | None = None
    ):
        self.metadata = Metadata() if metadata is None else metadata
        self.content = [] if content is None else content

    def add_content(self, tag: Tag, content: str):
        self.content.append((tag, content))
