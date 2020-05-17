""" This file does all the legwork for the site generation.
    It contains everything except the custom markdown extensions.
    buildSite() is the main method; call it to build the site in the pwd.
"""

import os
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown
from markdown_katex import KatexExtension
import toml

from .mdExtensions.admonition import AdmonitionExtension
from .mdExtensions.meta import MetaExtension
from .globals import *
from .config_structs import *


def readSiteFiles(groups, md):
    """ Goes through the folders listed in the config
        and reads all the markdown files in them.

        Arguments:
            groups is a list of PagesConfigs
            md is a Markdown renderer object

        Returns a list of PageInfo structs
    """
    global PAGE_EXTENSION
    content = {}

    for group in groups:
        filesList = []
        for path in group.files:
            if not os.path.isfile(path):
                print(f"Couldn't find file {path}")
                raise FileNotFoundError
            fileContent = loadPage(path, md, PAGE_EXTENSION)
            fileContent.group = group.groupName
            filesList.append(fileContent)

        for topDir in group.directories:
            for (dirPath, _, childFiles) in os.walk(topDir):
                for filename in childFiles:
                    path = os.path.join(dirPath, filename)
                    if not os.path.isfile(path):
                        print(f"Couldn't find file {path}")
                        raise FileNotFoundError
                    fileContent = loadPage(path, md, PAGE_EXTENSION)
                    fileContent.group = group.groupName
                    filesList.append(fileContent)

        if group.sortByDate:
            filesList.sort(
                key=lambda x: x.date, reverse=group.sortReverse,
            )
        content[group.groupName] = filesList

    return content


def loadPage(path, md, pageExtension):
    """ Loads a markdown file and parses it into a dict of info.
    """
    with open(path) as f:
        body = f.read()

    html = md.convert(body)
    meta = md.Meta
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    slug = os.path.splitext(basename)[0]

    if "path" in meta:
        url = os.path.join(meta["path"], slug) + pageExtension
    else:
        url = os.path.join(dirname, slug) + pageExtension

    fileContent = PageInfo(
        meta,
        path=path,
        slug=slug,
        url=url,
        content=html,
    )
    return fileContent


def buildAssetFiles(*, assetsConfig, buildConfig):
    """ Copies asset files into the output directory.
    """
    buildDir = buildConfig.buildDirectory
    try:
        for f in assetsConfig.files:
            os.makedirs(os.path.join(buildDir, os.path.dirname(f)), exist_ok=True)
            shutil.copy(f, os.path.join(buildDir, f))
    except KeyError:
        pass
    try:
        for d in assetsConfig.directories:
            for f in os.listdir(d):
                if os.path.isfile(os.path.join(d, f)):
                    os.makedirs(os.path.join(buildDir, d), exist_ok=True)
                    shutil.copy(os.path.join(d, f), os.path.join(buildDir, d, f))
    except KeyError:
        pass


def buildContentFiles(*, buildConfig, siteConfig, content, templates):
    """ This renders the pages from the templates and writes them
        into the output directory.
    """

    buildDir = buildConfig.buildDirectory
    groupsData = {}
    for groupName, group in content.items():
        groupsData[groupName] = list(map(PageInfo.forTemplate, group))
    pagesData = {}
    for _, group in content.items():
        for item in group:
            pagesData[item.slug] = item

    for _, group in content.items():
        for page in group:
            rendered = templates[page.template].render(
                {
                    "site": siteConfig,
                    "pages": pagesData,
                    "groups": groupsData,
                    "currentPage": page.forTemplate(),
                }
            )
            path = os.path.join(buildDir, page.url)
            if not os.path.isdir(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, "w") as f:
                f.write(rendered)


def loadTempates(templateConfig):
    templates = {}
    env = Environment(loader=FileSystemLoader(os.curdir))
    for f in templateConfig.files:
        templates[os.path.basename(f)] = env.get_template(f)
    for d in templateConfig.directories:
        env = Environment(loader=FileSystemLoader(d))
        for f in os.listdir(d):
            templates[f] = env.get_template(f)
    return templates


def buildSite(silent=False):
    """ The main function.
        Loads configs and builds the website in the pwd.
    """
    # load config
    global CONFIG_FILE_PATH
    with open(CONFIG_FILE_PATH) as f:
        config = toml.loads(f.read())
    assetsConfig = FilesConfig(config["assets"])
    buildConfig = BuildConfig(config["build"])
    pagesConfig = parseGroups(config["pages"])
    siteConfig = SiteConfig(config["site"])
    templateConfig = FilesConfig(config["templates"])

    # Load templates
    templates = loadTempates(templateConfig)

    # init markdown system
    md = markdown.Markdown(
        extensions=[
            "fenced_code",
            "tables",
            "codehilite",
            "smarty",
            "sane_lists",
            MetaExtension(),
            AdmonitionExtension(),
            KatexExtension(),
        ]
    )

    # clear output directory
    if os.path.exists(buildConfig.buildDirectory):
        shutil.rmtree(buildConfig.buildDirectory)
    else:
        os.mkdir(buildConfig.buildDirectory)

    content = readSiteFiles(pagesConfig, md)
    enrichSiteConfig(siteConfig, content)
    buildAssetFiles(assetsConfig=assetsConfig, buildConfig=buildConfig)
    buildContentFiles(
        buildConfig=buildConfig,
        siteConfig=siteConfig,
        content=content,
        templates=templates,
    )


# Sets the `groups` and `tags` fields in the site config
def enrichSiteConfig(siteConfig, content):
    groups = set()
    tags = set()
    for (name, group) in content.items():
        groups.add(name)
        for page in group:
            for tag in page.tags:
                tags.add(tag)
    siteConfig.groups = sorted(list(groups))
    siteConfig.tags = sorted(list(tags))
