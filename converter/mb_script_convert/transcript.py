from dataclasses import dataclass, fields
from typing import Literal, Optional

type Tag = Literal["direction", "character", "parenthetical", "dialogue", "end"]
type Content = list[tuple[Tag, str]]


type HugoFrontmatter = dict[str, str | HugoFrontmatter]


@dataclass
class Metadata:
    episode_title: Optional[str] = None
    series: Optional[str] = None
    season: Optional[int] = None
    season_episode_number: Optional[int] = None
    date_published: Optional[str] = None
    cover_url: Optional[str] = None

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


class Transcript:
    """
    Represents a transcript in a format agnostic way.
    Used as an intermediate step when converting.
    """

    content: Content
    metadata: Metadata

    def __init__(self, metadata: Metadata = Metadata(), content: Content = []):
        self.metadata = metadata
        self.content = content

    def add_content(self, tag: Tag, content: str):
        self.content.append((tag, content))
