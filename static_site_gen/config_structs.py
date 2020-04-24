""" A bunch of dataclasses which are used to hold the config data
"""

from typing import Any, Dict, List, Optional


@dataclass
class SiteConfig:
    title: str
    subtitle: str
    description: str

    def __init__(self, map: Dict[str, Any]):
        super().__init__(map)
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
        super().__init__(map)
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
        super().__init__(map)
        try:
            self.files = map["files"]
            self.files = map["directories"]
        except KeyError as e:
            print(f"Config error: bad key {e}")
            raise


@dataclass
class PagesConfig(FilesConfig):
    sortBy: Optional[str]
    sortByReverse: Optional[str]

    def __init__(self, map: Dict[str, Any]):
        super().__init__(map)
        self.sortBy = map["sortBy"] if "sortBy" in map else None
        self.sortByReverse = map["sortByReverse"] if "sortByReverse" in map else None
