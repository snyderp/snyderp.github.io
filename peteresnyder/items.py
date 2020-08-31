import datetime
import html
import json
import pathlib
from typing import Any, Dict, Literal, List, Optional

from peteresnyder.types import Url, Source


DATE_FORMAT = "%b %d, %Y"
PRESS_ITEM_TYPES = ["news", "podcast", "radio"]


class Item:
    date: datetime.datetime
    title: str
    url: Url

    def __init__(self, date: datetime.datetime, title: str, url: Url) -> None:
        self.date = date
        self.title = title
        self.url = url

    def to_html(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def list_to_html(items: List["Item"]) -> str:
        raise NotImplementedError()

    @staticmethod
    def list_from_json(data: Dict[str, Any]) -> List["Item"]:
        raise NotImplementedError()

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "Item":
        date_str = item_data["date"]
        date = datetime.datetime.fromisoformat(date_str)
        return Item(date, item_data["title"], item_data["url"])


class PressItem(Item):
    source: Source
    type: str

    def __init__(self, date: datetime.datetime, title: str, url: Url,
                 source: Source, item_type: str) -> None:
        self.source = source
        if item_type not in PRESS_ITEM_TYPES:
            raise ValueError(f"{item_type} is not a valid PressItem type")
        self.type = item_type
        super().__init__(date, title, url)

    def to_html(self) -> str:
        title_line = (
            f"\t<a class='pub-title' href='{self.url}'>" +
            html.escape(self.title) +
            "</a>"
        )

        venue_line = (
            "<span class='venue'>" +
            f"<a href='{self.source.url}'>" +
            html.escape(self.source.title) +
            "</a>" +
            "<span class='date'>" +
            self.date.strftime(DATE_FORMAT) +
            "</span>" +
            "</span>"
        )

        type_line = (
            "<span class='pub-type'>" +
            html.escape(self.type) +
            "</span>"
        )
        return "\n".join([title_line, venue_line, type_line])

    @staticmethod
    def list_to_html(items: List["Item"]) -> str:
        item_html = []
        for item in items:
            item_html.append("<li>" + item.to_html() + "</li>")
        html = (
            "<ul class='publications publications-press'>\n" +
            "\n".join(item_html) +
            "</ul>"
        )
        return html

    @staticmethod
    def list_from_json(data: Dict[str, Any]) -> List["PressItem"]:
        items: List["PressItem"] = []
        for item in data["items"]:
            items.append(PressItem.item_from_json(item, data))
        return items

    @staticmethod
    def item_from_json(item_data: Dict[str, Any],
                       all_data: Dict[str, Any]) -> "PressItem":
        basic_item = Item.item_from_json(item_data, all_data)
        source_abbr = item_data["source"]
        source_data = all_data["abbrs"]["sources"][source_abbr]
        source = Source(source_data["title"], source_data["url"])
        return PressItem(basic_item.date, basic_item.title, basic_item.url,
                         source, item_data["type"])


def press_items_from_data(path: pathlib.Path) -> List[PressItem]:
    items: List[PressItem] = []
    full_data = json.load(path.open())
    for item_data in full_data["items"]:
        item = PressItem.item_from_json(item_data, full_data)
        items.append(item)
    return items
