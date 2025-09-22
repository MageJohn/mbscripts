from dataclasses import dataclass, fields
from typing import Literal, Optional, Any, TypeVar, Self, cast
import logging

logger = logging.getLogger(__name__)

type Tag = Literal["direction", "character", "parenthetical", "dialogue", "end"]
type Content = list[tuple[Tag, str]]


type HugoFrontmatter = dict[str, str | HugoFrontmatter]


@dataclass
class Metadata:
    episode_title: Optional[str] = None
    series: Optional[str] = None
    season: Optional[str] = None
    season_episode_number: Optional[str] = None
    date_published: Optional[str] = None
    cover_url: Optional[str] = None

    def merge(self, other: Self):
        for field in fields(self):
            if getattr(self, field.name) is None:
                setattr(self, field.name, getattr(other, field.name))

    def to_hugo_frontmatter(self) -> HugoFrontmatter:
        params = {}
        frontmatter: HugoFrontmatter = {"params": params}
        for field in fields(self):
            name, value = field.name, getattr(self, field.name)
            if value is None:
                continue
            match name:
                case "episode_title":
                    frontmatter["title"] = value
                case "date_published":
                    frontmatter["date"] = value
                case _:
                    params[name] = value
        return frontmatter

    @classmethod
    def from_hugo_frontmatter(cls, frontmatter: dict[str, Any]) -> Self:
        m = cls()

        params = _checked_get(frontmatter, "params", dict)
        if params is None:
            params = {}
        for field in fields(m):
            match field.name:
                case "episode_title":
                    m.episode_title = _checked_get(frontmatter, "title", str)
                case "date_published":
                    m.date_published = _checked_get(frontmatter, "date", str)
                case _:
                    setattr(m, field.name, _checked_get(params, field.name, cast(type, field.type)))
        return m


T = TypeVar("T")


def _checked_get(frontmatter: dict[str, Any], key: str, type_: type[T]) -> T | None:
    value = frontmatter.get(key)
    if isinstance(value, type_):
        return value
    elif value is None:
        return None
    else:
        logger.warning(
            f"Invalid type for field {key} when loading frontmatter. Expected {type_}, got {type(value)}."
        )


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
