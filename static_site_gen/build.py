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


def readSiteFiles(contentFiles, md):
    """ Goes through the folders listed in the config
        and reads all the markdown files in them.

        Args:
            contentFiles, a dict formatted as
                contentFiles:
                    "pages":    # markdown files to be turned into pages
                        "files": []     # loose md files to be rendered into pages
                        "directories": []   # a list of directories containing md files.
                                            # files in the same dir will be grouped
                                            # into lists in the Jinja templates.
                    "assets":   # assets used by the website
                        "files": []     # loose asset files used by the site
                        "directories": []   # directories containing asset files
                                            # these are not meaningfully grouped by directory
            md, a markdown renderer instance

        Returns:
            a dict formatted as
                returnValue:
                    "pages":
                        <fileName>: <pageData>  # pageDatas are dicts of info
                                                # they include file contents and metadata
                        <dirName>: [<pageData>] # markdown files grouped in dirs are stored in lists
                    "assets":
                        <fileName>: <assetPaths>    # assetPaths are just the full path to the file
                        <dirName>: [<assetPath>]    # assets grouped in dirs are stored in lists
    """
    content = {}
    # fileType == "pages" means this file / directory of files is markdown
    # fileType == "assets" means it's an asset that is not modified by the SSG
    for fileType, fileCollection in contentFiles.items():
        content[fileType] = {}
        # Loose files which are not grouped into a directory
        if "files" in fileCollection:
            for path in fileCollection["files"]:
                name = os.path.splitext(os.path.basename(path))[0]
                data = (
                    loadPage(path, md)
                    if fileType == "pages"
                    else os.path.join(path, name)
                )
                content[fileType][name] = data

        # files grouped together in directories
        if "directories" in fileCollection:
            for dirPath in fileCollection["directories"]:
                dirFiles = []
                for fileOrDir in os.listdir(dirPath):
                    path = os.path.join(dirPath, fileOrDir)
                    if os.path.isfile(path):
                        data = (
                            loadPage(path, md)
                            if fileType == "pages"
                            else os.path.join(path, fileOrDir)
                        )
                        dirFiles.append(data)

                if fileType == "pages":  # sort pages in dir if necessary
                    if "sortBy" in fileCollection:
                        dirFiles.sort(key=lambda x: x[fileCollection["sortBy"]])
                    elif "sortByReverse" in fileCollection:
                        dirFiles.sort(
                            key=lambda x: x[fileCollection["sortByReverse"]],
                            reverse=True,
                        )
                content[fileType][path] = dirFiles
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
        raise KeyError  # TODO better error handling
    meta["content"] = html
    return meta


def buildAssetFiles(fileConfig, buildConfig):
    """ Copies asset files into the output directory.
    """
    buildDir = buildConfig["buildDirectory"]
    try:
        for f in fileConfig["assets"]["files"]:
            os.makedirs(os.path.join(buildDir, os.path.dirname(f)), exist_ok=True)
            shutil.copy(f, os.path.join(buildDir, f))
    except KeyError:
        pass
    try:
        for d in fileConfig["assets"]["directories"]:
            for f in os.listdir(d):
                if os.path.isfile(os.path.join(d, f)):
                    os.makedirs(os.path.join(buildDir, d), exist_ok=True)
                    shutil.copy(os.path.join(d, f), os.path.join(buildDir, d, f))
    except KeyError:
        pass


def buildContentFiles(siteConfig, content, templates, buildConfig):
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

    buildDir = buildConfig["buildDirectory"]
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
    siteConfig = config["site"]
    templateConfig = config["templates"]
    fileConfig = config["files"]
    buildConfig = config["build"]

    # Load templates
    templates = {}
    for d in templateConfig["directories"]:
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
    if os.path.exists(buildConfig["buildDirectory"]):
        shutil.rmtree(buildConfig["buildDirectory"])
    else:
        os.mkdir(buildConfig["buildDirectory"])

    content = readSiteFiles(fileConfig, md)  # read in assets and pages
    buildAssetFiles(fileConfig, buildConfig)  # copy assets into build dir
    buildContentFiles(
        siteConfig, content, templates, buildConfig
    )  # render pages into build dir
