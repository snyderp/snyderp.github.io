import collections


Url = str


class Source:
    title: str
    url: Url

    def __init__(self, title: str, url: Url) -> None:
        self.title = title
        self.url = url
