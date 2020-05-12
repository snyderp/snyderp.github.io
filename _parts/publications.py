import enum
import html
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class VenueRefType(enum.Enum):
    ABBR = 1
    URL = 2


class PublicationRecord:
    title: str
    url: str,
    authors: List[str]
    venue: str
    venue_type: VenueRefType
    year: int
    links: Optional[Dict[str, str]]

    @staticmethod
    def venue_info(venue_ref: str, )

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