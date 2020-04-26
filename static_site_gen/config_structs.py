""" A bunch of dataclasses which are used to hold the config data
"""

from dataclasses import dataclass
import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SiteConfig:
    title: str
    subtitle: str
    description: str

    def __init__(self, map: Dict[str, Any]):
        try:
            self.title = map["title"]
            self.subtitle = map["subtitle"]
            self.description = map["description"]
        except KeyError as e:
            print(f"Config error: bad key {e}")
            raise


@dataclass
class BuildConfig:
    buildDirectory: str

    def __init__(self, map: Dict[str, Any]):
        try:
            self.buildDirectory = map["buildDirectory"]
        except KeyError as e:
            print(f"Config error: bad key {e}")
            raise


@dataclass
class FilesConfig:
    files: List[str]
    directories: List[str]

    def __init__(self, map: Dict[str, Any]):
        self.files = map["files"] if "files" in map else []
        self.directories = map["directories"] if "directories" in map else []


@dataclass
class PagesConfig(FilesConfig):
    sortByDate: bool
    sortByReverse: bool
    groupName: str

    def __init__(self, map: Dict[str, Any], groupName=None):
        super().__init__(map)
        self.sortByDate = map["sortBy"] if "sortBy" in map else False
        self.sortReverse = map["sortReverse"] if "sortByReverse" in map else False


def parseGroups(groupsDict):
    groups = []
    for key, val in groupsDict.items():
        pc = PagesConfig(val)
        pc.groupName = key
        groups.append(pc)
    return groups


@dataclass
class ContentFile:
    title: str
    date: datetime.date
    description: str
    template: Any
    content: str
    path: str
    slug: str
    url: str
    group: str

    def __init__(self, map, *, path, slug, url, content, group=None):
        self.title = map["title"] if "title" in map else None
        self.date = map["date"] if "date" in map else None
        self.description = map["description"] if "description" in map else None
        self.template = map["template"] if "template" in map else None
        self.slug = slug
        self.content = content
        self.path = path
        self.url = url
        self.group = group

    def forTemplate(self):
        return {
            "title": self.title,
            "date": self.date,
            "description": self.description,
            "content": self.content,
            "url": self.url,
            "group": self.group,
        }
