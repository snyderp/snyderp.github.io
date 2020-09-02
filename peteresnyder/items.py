import datetime
import html
import json
from operator import attrgetter
import pathlib
from typing import Any, Dict, Generic, Literal, List, Optional, TypeVar

from .types import Author, Html, Url, Source


def authors_html(authors: List[Author]) -> Html:
    inner_items = [f"<li>{a.to_html()}</li>" for a in authors]
    return (
        "<ol class='authors'>" +
        "\n\t".join(inner_items) +
        "</ol>"
    )


class Item:
    html_classes = ["publications"]
    date: datetime.datetime
    title: str
    url: Url

    def __init__(self, date: datetime.datetime, title: str, url: Url) -> None:
        self.date = date
        self.title = title
        self.url = url

    def title_html(self) -> Html:
        return (
            f"\t<a class='pub-title' href='{self.url}'>" +
            html.escape(self.title) +
            "</a>"
        )

    def date_html(self) -> Html:
        return (
            "<span class='date'>" +
            self.date.strftime("%b %d, %Y") +
            "</span>"
        )

    def to_html(self) -> Html:
        raise NotImplementedError()

    @staticmethod
    def sort(items: List["Item"]) -> List["Item"]:
        return sorted(items, key=attrgetter("date"), reverse=True)

    @classmethod
    def list_to_html(cls, items: List["Item"]) -> Html:
        item_html = []
        for item in items:
            item_html.append("<li>" + item.to_html() + "</li>")

        class_str = " ".join(cls.html_classes)
        html = (
            f"<ul class='{class_str}'>" +
            " ".join(item_html) +
            "</ul>"
        )
        return html

    @classmethod
    def list_from_json(cls, data: Dict[str, Any]) -> List["Item"]:
        items: List["Item"] = []
        for item in data["items"]:
            items.append(cls.item_from_json(item, data))
        return items

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "Item":
        date_str = item_data["date"]
        date = datetime.datetime.fromisoformat(date_str)
        return Item(date, item_data["title"], item_data["url"])


class BlogItem(Item):
    authors: List[Author]
    html_classes = ["publications", "publications-blog"]
    source: Source

    def __init__(self, date: datetime.datetime, title: str, url: Url,
                 source: Source, authors: List[Author]) -> None:
        self.source = source
        self.authors = authors
        super().__init__(date, title, url)

    def venue_html(self) -> Html:
        return (
            "<span class='venue'>" +
            self.source.to_html() +
            self.date_html() +
            "</span>"
        )

    def to_html(self) -> Html:
        title_line = self.title_html()
        authors_line = authors_html(self.authors)
        venue_line = self.venue_html()
        return "".join([title_line, authors_line, venue_line])

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "BlogItem":
        basic_item = Item.item_from_json(item_data, all_data)

        authors = []
        for author in item_data["authors"]:
            if author[0] == "@":
                author_title = all_data["abbrs"]["authors"][author]
                authors.append(Author(author_title, author))
            else:
                authors.append(Author(author))

        source_abbr = item_data["source"]
        source_data = all_data["abbrs"]["sources"][source_abbr]
        source = Source(source_abbr, source_data["title"], source_data["url"])
        return BlogItem(basic_item.date, basic_item.title, basic_item.url,
                        source, authors)


class PressItem(BlogItem):
    PRESS_ITEM_TYPES = ["news", "podcast", "radio"]
    html_classes = ["publications", "publications-press"]

    source: Source
    type: str

    def __init__(self, date: datetime.datetime, title: str, url: Url,
                 source: Source, item_type: str) -> None:
        if item_type not in PressItem.PRESS_ITEM_TYPES:
            raise ValueError(f"{item_type} is not a valid PressItem type")
        self.type = item_type
        super().__init__(date, title, url, source, [])

    def to_html(self) -> Html:
        title_line = self.title_html()
        venue_line = self.venue_html()
        type_line = (
            "<span class='pub-type'>" +
            html.escape(self.type) +
            "</span>"
        )
        return "".join([title_line, venue_line, type_line])

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "PressItem":
        basic_item = Item.item_from_json(item_data, all_data)
        source_abbr = item_data["source"]
        source_data = all_data["abbrs"]["sources"][source_abbr]
        source = Source(source_abbr, source_data["title"], source_data["url"])
        return PressItem(basic_item.date, basic_item.title, basic_item.url,
                         source, item_data["type"])

# T = TypeVar('T')
# def items_from_data(path: pathlib.Path, cls: T) -> List[T]:
#     items: List[T] = []
#     full_data = json.load(path.open())
#     for item_data in full_data["items"]:
#         item = T.item_from_json(item_data, full_data)
#         items.append(item)
#     return items
