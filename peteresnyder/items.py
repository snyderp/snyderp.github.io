import dataclasses
import datetime
import html
import json
from operator import attrgetter
import pathlib
from typing import Any, cast, Dict, Generic, Literal, List
from typing import Optional, TypeVar, Union

from .types import Author, Date, Html, Link, Source, Url, Venue, Year


def authors_html(authors: List[Author]) -> Html:
    inner_items = [f"<li>{a.to_html()}</li>" for a in authors]
    return (
        "<ol class='authors'>" +
        "".join(inner_items) +
        "</ol>"
    )


def links_html(links: List[Link]) -> Html:
    if len(links) == 0:
        return ""
    inner_items = [f"<li>{link.to_html()}</li>" for link in links]
    return (
        "<ul class='pub-links'>" +
        "".join(inner_items) +
        "</ul>"
    )


def destination_url(dest: Union[Source, Venue], list_item: "ListItem") -> Html:
    return (
        "<span class='venue'>" +
        dest.to_html() +
        list_item.date_html() +
        "</span>"
    )


def authors_from_json(item_data: Dict[str, Any],
                      all_data: Dict[str, Any]) -> List[Author]:
    authors = []
    for author in item_data["authors"]:
        if author[0] == "@":
            author_title = all_data["abbrs"]["authors"][author]
            authors.append(Author(author_title, author))
        else:
            authors.append(Author(author))
    return authors


def source_from_json(item_data: Dict[str, Any],
                     all_data: Dict[str, Any]) -> Source:
    source_abbr = item_data["source"]
    source_data = all_data["abbrs"]["sources"][source_abbr]
    return Source(source_data["title"], source_data["url"], source_abbr)


def venue_from_json(item_data: Dict[str, Any],
                    all_data: Dict[str, Any]) -> Venue:
    raw_venue = item_data["venue"]
    if raw_venue[0] == "@":
        return Venue(**all_data["abbrs"]["venues"][raw_venue])
    return Venue(raw_venue)


def date_from_json(item_data: Dict[str, Any]) -> datetime.datetime:
    date_str = item_data["date"]
    return datetime.datetime.fromisoformat(date_str)


def links_from_json(item_data: Dict[str, Any]) -> List[Link]:
    try:
        links_data = item_data["links"]
        return [Link(k, v) for k, v in links_data.items()]
    except KeyError:
        return []


class BaseItem:
    html_classes: List[str] = []

    def to_html(self) -> Html:
        raise NotImplementedError()

    @staticmethod
    def sort(items: List["BaseItem"]) -> List["BaseItem"]:
        return sorted(items, key=attrgetter("date"), reverse=True)

    @classmethod
    def list_to_html(cls, items: List["BaseItem"]) -> Html:
        item_html = []
        for item in items:
            item_html.append("<li>" + item.to_html() + "</li>")

        class_str = " ".join(cls.html_classes)
        html = (
            f"<ul class='{class_str}'>" +
            "".join(item_html) +
            "</ul>"
        )
        return html

    @classmethod
    def list_from_json(cls, data: Dict[str, Any]) -> List["BaseItem"]:
        items: List["BaseItem"] = []
        for item in data["items"]:
            items.append(cls.item_from_json(item, data))
        return items

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "BaseItem":
        raise NotImplementedError()


class ListItem(BaseItem):
    html_classes = ["publications"]
    date: Date
    title: str
    url: Optional[Url]

    def __init__(self, date: Date, title: str, url: Optional[Url]) -> None:
        self.date = date
        self.title = title
        self.url = url

    def title_html(self) -> Html:
        safe_title = html.escape(self.title)
        if self.url:
            return f"<a class='pub-title' href='{self.url}'>{safe_title}</a>"
        return f"<span class='pub-title'>{safe_title}</span>"

    def date_html(self) -> Html:
        date_line = ""
        try:
            date_as_datetime = cast(datetime.datetime, self.date)
            date_line = date_as_datetime.strftime("%b %d, %Y")
        except AttributeError:
            date_line = str(self.date)
        return f"<span class='year'>{date_line}</span>"


class BlogItem(ListItem):
    html_classes = ["publications", "publications-blog"]

    source: Source
    authors: List[Author]

    def __init__(self, date: Date, title: str, url: Url,
                 source: Source, authors: List[Author]) -> None:
        self.authors = authors
        self.source = source
        super().__init__(date, title, url)

    def to_html(self) -> Html:
        title_line = self.title_html()
        authors_line = authors_html(self.authors)
        dest_url = destination_url(self.source, self)
        return "".join([title_line, authors_line, dest_url])

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "BlogItem":
        date = date_from_json(item_data)
        authors = authors_from_json(item_data, all_data)
        source = source_from_json(item_data, all_data)
        return BlogItem(date, item_data["title"], item_data["url"],
                        source, authors)


@dataclasses.dataclass
class PublicationItem(ListItem):
    authors: List[Author]
    links: List[Link]
    venue: Venue

    def __init__(self, year: Year, title: str, url: Optional[Url],
                 authors: List[Author], links: List[Link],
                 venue: Venue) -> None:
        self.authors = authors
        self.links = links
        self.venue = venue
        super().__init__(year, title, url)

    def to_html(self) -> Html:
        title_line = self.title_html()
        authors_line = authors_html(self.authors)
        dest_html = destination_url(self.venue, self)
        links_link = links_html(self.links)
        return "".join([title_line, authors_line, dest_html, links_link])

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "PublicationItem":
        year = item_data["year"]
        authors = authors_from_json(item_data, all_data)
        links = links_from_json(item_data)
        venue = venue_from_json(item_data, all_data)
        url = item_data["url"] if "url" in item_data else None
        return PublicationItem(year, item_data["title"], url, authors,
                               links, venue)


@dataclasses.dataclass
class InvolvementItem(BaseItem):
    venue: Venue
    position: str
    date: Year

    def to_html(self) -> Html:
        return (
            "<tr>"
            f'<td class="venue">{self.venue.to_html()}</td>'
            f'<td class="position">{html.escape(self.position)}</td>'
            f'<td class="year">{self.date}</td>'
            "</tr>"
        )

    @classmethod
    def list_to_html(cls, items: List["BaseItem"]) -> Html:
        return "\n".join((x.to_html() for x in items))

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "InvolvementItem":
        raw_venue = item_data["venue"]
        if raw_venue[0] == "@":
            venue = Venue(**all_data["abbrs"]["venues"][raw_venue])
        else:
            venue = Venue(raw_venue)

        raw_position = item_data["position"]
        position = all_data["abbrs"]["positions"][raw_position]
        date = item_data["year"]
        return InvolvementItem(venue, position, date)


class PressItem(ListItem):
    PRESS_ITEM_TYPES = ["news", "podcast", "radio"]
    html_classes = ["publications", "publications-press"]

    source: Source
    type: str

    def __init__(self, date: datetime.datetime, title: str, url: Url,
                 source: Source, item_type: str) -> None:
        if item_type not in PressItem.PRESS_ITEM_TYPES:
            raise ValueError(f"{item_type} is not a valid PressItem type")
        self.source = source
        self.type = item_type
        super().__init__(date, title, url)

    def to_html(self) -> Html:
        title_line = self.title_html()
        venue_line = destination_url(self.source, self)
        type_line = (
            "<span class='pub-type'>" +
            html.escape(self.type) +
            "</span>"
        )
        return "".join([title_line, venue_line, type_line])

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "PressItem":
        date = date_from_json(item_data)
        source = source_from_json(item_data, all_data)
        return PressItem(date, item_data["title"], item_data["url"],
                         source, item_data["type"])
