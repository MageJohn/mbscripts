from typing import Literal

type Tag = Literal["direction", "character", "parenthetical", "dialogue", "end"]
type Content = list[tuple[Tag, str]]
type Metadata = dict[str, str | Metadata]


class Transcript:
    """
    Represents a transcript in a format agnostic way.
    Used as an intermediate step when converting.
    """

    content: Content
    metadata: Metadata

    def __init__(self, metadata: Metadata = {}, content: Content = []):
        self.metadata = metadata
        self.content = content

    def add_content(self, tag: Tag, content: str):
        self.content.append((tag, content))

    def set_metadata(self, key: str, value: str):
        self.metadata[key] = value
