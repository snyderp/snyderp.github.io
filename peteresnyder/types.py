import collections
import html
from typing import Optional

Html = str
Url = str


class Author:
    title: str
    abbr: Optional[str]

    def __init__(self, title: str, abbr: Optional[str] = None) -> None:
        self.abbr = abbr
        self.title = title

    def to_html(self) -> Html:
        if self.abbr == "@me":
            return f"<span class='me'>{html.escape(self.title)}</span>"
        return html.escape(self.title)


class Source:
    title: str
    url: Url
    abbr: str

    def __init__(self, abbr: str, title: str, url: Url) -> None:
        self.abbr = abbr
        self.title = title
        self.url = url

    def to_html(self) -> Html:
        return (
            f"<a href='{self.url}' class='source source-{self.abbr[1:]}'>" +
            html.escape(self.title) +
            "</a>"
        )
