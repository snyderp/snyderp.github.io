import collections
import dataclasses
import html
from typing import Optional

Html = str
Url = str


@dataclasses.dataclass
class Author:
    title: str
    abbr: Optional[str] = None

    def to_html(self) -> Html:
        if self.abbr == "@me":
            return f"<span class='me'>{html.escape(self.title)}</span>"
        return html.escape(self.title)


@dataclasses.dataclass
class Source:
    title: str
    url: Url
    abbr: str

    def to_html(self) -> Html:
        return (
            f"<a href='{self.url}' class='source source-{self.abbr[1:]}'>" +
            html.escape(self.title) +
            "</a>"
        )


@dataclasses.dataclass
class Venue:
    title: str
    abbr: Optional[str] = None
    suffix: Optional[str] = None

    def to_html(self) -> Html:
        esc_title = html.escape(self.title)
        html_str = ""
        if self.abbr:
            esc_abbr = html.escape(self.abbr)
            html_str += f'<abbr title="{esc_title}">{esc_abbr}</abbr>'
        else:
            html_str += esc_title

        if self.suffix:
            html_str += " " + html.escape(self.suffix)

        return html_str
