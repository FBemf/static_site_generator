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


def readSiteFiles(fileCollection, isMarkdown, md):
    """ Goes through the folders listed in the config
        and reads all the markdown files in them.

        Returns:
            a dict formatted as either
                isMarkdown=True:
                    <fileName>: <pageData>  # pageDatas are dicts of info
                                            # they include file contents and metadata
                    <dirName>: [<pageData>] # markdown files grouped in dirs are stored in lists
                isMarkdown=False:
                    <fileName>: <assetPaths>    # assetPaths are just the full path to the file
                    <dirName>: [<assetPath>]    # assets grouped in dirs are stored in lists
    """
    content = {}

    for path in fileCollection.files:
        name = os.path.splitext(os.path.basename(path))[0]
        data = loadPage(path, md) if isMarkdown else os.path.join(path, name)
        content[name] = data

    for dirPath in fileCollection.directories:
        dirFiles = []
        for relativePath in os.listdir(dirPath):
            absolutePath = os.path.join(dirPath, relativePath)
            if os.path.isfile(absolutePath):
                data = (
                    loadPage(absolutePath, md)
                    if isMarkdown
                    else os.path.join(absolutePath, relativePath)
                )
                dirFiles.append(data)

        if isMarkdown:
            if fileCollection.sortBy:
                dirFiles.sort(
                    key=lambda x: x[fileCollection.sortBy],
                    reverse=fileCollection.sortReverse,
                )
        content[dirPath] = dirFiles
    return content


def loadPage(path, md):
    """ Loads a markdown file and parses it into a dict of info.
    """
    with open(path) as f:
        body = f.read()
    html = md.convert(body)
    meta = md.Meta
    meta["url"] = os.path.splitext(path)[0] + ".html"
    if "content" in meta:
        print(meta)
        raise KeyError  # TODO better error handling
    meta["content"] = html
    return meta


def buildAssetFiles(assetsConfig, buildConfig):
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


def buildContentFiles(buildConfig, siteConfig, content, templates):
    """ This renders the pages from the templates and writes them
        into the output directory.
    """

    def buildOneFile(page):
        rendered = templates[page["template"]].render(
            {"site": siteConfig, **content, "currentPage": page}
        )
        url = page["url"]
        os.makedirs(os.path.join(buildDir, os.path.dirname(url)), exist_ok=True)
        with open(f"{buildDir}/{url}", "w") as f:
            f.write(rendered)

    buildDir = buildConfig.buildDirectory
    for _, fileOrFileList in content["pages"].items():
        # if it's a list of file names from the same directory
        if type(fileOrFileList) == list:
            for page in fileOrFileList:
                buildOneFile(page)
        else:  # it's just a file name
            buildOneFile(fileOrFileList)


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
    pagesConfig = PagesConfig(config["pages"])
    siteConfig = SiteConfig(config["site"])
    templateConfig = FilesConfig(config["templates"])

    # Load templates
    templates = {}
    for d in templateConfig.directories:
        env = Environment(loader=FileSystemLoader(d))
        for f in os.listdir(d):
            templates[f] = env.get_template(f)

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

    content = {
        "assets": readSiteFiles(assetsConfig, False, md),
        "pages": readSiteFiles(pagesConfig, True, md),
    }
    buildAssetFiles(assetsConfig, buildConfig)  # copy assets into build dir
    buildContentFiles(
        buildConfig, siteConfig, content, templates
    )  # render pages into build dir
