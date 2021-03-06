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
    tags: str

    def __init__(self, map: Dict[str, Any], groups=None, tags=None):
        try:
            self.title = map["title"]
            self.subtitle = map["subtitle"]
            self.description = map["description"]
            self.groups = groups if groups else []
            self.tags = tags if tags else []
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
    sortReverse: bool
    groupName: str

    def __init__(self, map: Dict[str, Any], groupName=None):
        super().__init__(map)
        self.sortByDate = map["sortByDate"] if "sortByDate" in map else False
        self.sortReverse = map["sortReverse"] if "sortReverse" in map else False


def parseGroups(groupsDict):
    groups = []
    for key, val in groupsDict.items():
        pc = PagesConfig(val)
        pc.groupName = key
        groups.append(pc)
    return groups


@dataclass
class PageInfo:
    title: str
    author: str
    date: datetime.date
    updated: datetime.date
    description: str
    template: Any
    content: str
    tags: List[str]
    feed_id: str
    extra: Any
    slug: str
    content: str
    path: str
    url: str
    group: str

    def __init__(self, map, *, path, slug, url, content, group=None, iterateOver=None):
        self.title = map["title"] if "title" in map else None
        self.author = map["author"] if "author" in map else None
        self.date = map["date"] if "date" in map else None
        self.updated = map["updated"] if "updated" in map else None
        self.description = map["description"] if "description" in map else None
        self.template = map["template"] if "template" in map else None
        self.tags = map["tags"] if "tags" in map else []
        self.feed_id = map["feed_id"] if "feed_id" in map else []
        self.extra = map["extra"] if "extra" in map else None
        self.slug = slug
        self.content = content
        self.path = path
        self.url = url
        self.group = group

    def forTemplate(self):
        return {
            "title": self.title,
            "author": self.author,
            "date": self.date,
            "updated": self.updated,
            "description": self.description,
            "content": self.content,
            "url": self.url,
            "group": self.group,
            "tags": self.tags,
            "extra": self.extra,
        }

@dataclass
class FeedConfig:
    rssPath: str
    atomPath: str
    id: str
    link: str
    icon: str
    contributor: str
    logo: str
    language: str

    def __init__(self, map):
        self.rssPath = map["rssPath"]
        self.atomPath = map["atomPath"]
        self.id = map["id"]
        self.link = map["link"] if "link" in map else None
        self.icon = map["icon"] if "icon" in map else None
        self.contributor = map["contributor"] if "contributor" in map else None
        self.logo = map["logo"] if "logo" in map else None
        self.language = map["language"] if "language" in map else None