#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any, Dict

from peteresnyder.items import BlogItem, InvolvementItem
from peteresnyder.items import PressItem, PublicationItem


DATA_DIR = Path(".", "data")
TEMPLATE_DIR = DATA_DIR / Path("templates")
SECTIONS_DIR = DATA_DIR / Path("sections")
TEMPLATE_INDEX_HTML_TEXT = (TEMPLATE_DIR / Path("index.html")).read_text()

FILE_TYPE_MAPPING: Dict[str, Any] = {
    "press": PressItem,
    "blog": BlogItem,
    "involvement": InvolvementItem,
    "publications": PublicationItem,
}

for section_file in SECTIONS_DIR.iterdir():
    if section_file.stem not in FILE_TYPE_MAPPING:
        continue
    section_type = FILE_TYPE_MAPPING[section_file.stem]
    section_data = json.load(section_file.open())
    items = section_type.list_from_json(section_data)
    items_sorted = section_type.sort(items)
    section_html = section_type.list_to_html(items_sorted)
    TEMPLATE_INDEX_HTML_TEXT = TEMPLATE_INDEX_HTML_TEXT.replace(
        "{{" + section_file.stem + "}}", section_html)

print(TEMPLATE_INDEX_HTML_TEXT)