import enum
import html
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


FullData = Dict[str, str]
Html = str


class VenueRefType(enum.Enum):
    ABBR = 1
    URL = 2


class Venue:
    name: str
    ref_type: VenueRefType
    full_name: Optional[str]
    url: Optional[str]

    def __init__(self, short_name: str, desc: str):
        self.short_name = short_name
        if (desc.startswith("http:") or
            desc.startswith("https:") or
            desc.startswith("//")):
            self.ref_type = VenueRefType.URL
            self.url = desc
        else:
            self.ref_type = VenueRefType.ABBR
            self.full_name = desc

    def to_html(self) -> Html:
        if self.ref_type == VenueRefType.URL:
            return f"""
                <a href="{html.escape(self.url)}">
                    {html.escape(self.short_name, quotes=False)}
                </a>"""

        # VenueRefType.ABBR case
        return f"""
            <abbr title="{html.escape(self.full_name)}">
                {html.escape(self.short_name, quotes=False)}
            </abbr>"""


class AuthorAlias:
    alias: str
    full_name: str

    def __init__(self, alias: str, full_name: str):
        self.alias = alias
        self.full_name = full_name


class Author:
    name: str

    def __init__(self, name: str):
        self.name = name

    def is_me(self) -> bool:
        return self.ref == "@pes"

    def to_html(self) -> Html:
        return html.escape(self.name, quotes=False)






class DataSet:
    publications: List[Publications]
    venue: Dict[str, Venue]
    author_aliases: Dict[str, Author]

    def author_for_alias(self, author_ref: str) -> Optional[Author]:
        try:
            return self.author_aliases[author_ref]
        except KeyError:
            return None




class Publications:
    title: str
    url: str,
    authors: List[Author]
    venue: str
    year: int
    links: Optional[Dict[str, str]]

    @staticmethod
    def venue_info(venue_ref: str, dataset: FullData)

    @staticmethod
    def from_json(pub_item: Dict[str, Any],
                  dataset: Dict[str, Any]) -> PublicationRecord:
        pub = PublicationRecord()
        pub.title = pub_item["title"]
        pub.url = pub_item["url"]

        authors = []
        for author in pub_item["authors"]:
            if author.startswith("@"):
                authors.append(dataset["people"][author])
            else:
                authors.append(author)
        pub.authors = authors

        venue = dataset["venues"][pub_item["venue"]]
        if (venue.startswith("http:") or
            venue.startswith("https:") or
            venue.startswith("//")

def pub_to_html(data: dict[st], )


with open("publications.json", "r") as handle:
    data = json.load(handle)