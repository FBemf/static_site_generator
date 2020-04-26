""" A bunch of dataclasses which are used to hold the config data
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pprint


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
    sortBy: Optional[str]
    sortByReverse: Optional[str]

    def __init__(self, map: Dict[str, Any]):
        super().__init__(map)
        self.sortBy = map["sortBy"] if "sortBy" in map else None
        self.sortReverse = map["sortReverse"] if "sortByReverse" in map else False


@dataclass
class ContentFile:
    relativePath: str
    absPath: str
    isMarkdown: bool
    sortBy: bool
    sortReverse: bool
    meta: Dict[Any]
