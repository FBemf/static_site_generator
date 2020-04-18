""" This file handles the command line interface.

    Commands:
        init: create an example site in the pwd
        build: build the site in the pwd
"""

import os
import shutil

import click

from .build import buildSite


EXAMPLE_SITE_DIR = "../example-site"


@click.group()
def runCli():
    pass


@runCli.command()
@click.option("--quiet", help="Omit standard output." type=click.BOOL, default=False)
def init(quiet):
    """ Initialize the example site at the pwd
    """
    global EXAMPLE_SITE_DIR
    fileDir = os.path.dirname(os.path.abspath(__file__))
    full_example_path = os.path.join(fileDir, EXAMPLE_SITE_DIR)
    for fileOrDir in os.listdir(full_example_path):
        fullPath = os.path.join(full_example_path, fileOrDir)
        if os.path.isfile(fullPath):
            shutil.copy2(fullPath, fileOrDir)
        elif os.path.isdir(fullPath):
            shutil.copytree(fullPath, fileOrDir)
    if not quiet:
        print("Example site built.")


@runCli.command()
@click.option("--quiet", help="Omit standard output." type=click.BOOL, default=False)
def build(quiet):
    """ Builds the site in the pwd
    """

    buildSite()

    if not quiet:
        print("Finished building successfully.")
