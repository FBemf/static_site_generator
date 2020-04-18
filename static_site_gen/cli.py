""" This file handles the command line interface.

    Commands:
        init: create an example site in the pwd
        build: build the site in the pwd
"""

import http.server
import socketserver
import os
import shutil
import toml

import click

from .build import buildSite
from .globals import *


@click.group()
def runCli():
    pass


@runCli.command()
@click.option("--quiet", help="Omit standard output.", type=click.BOOL, default=False)
def init(quiet):
    """ Initialize the example site at the current working directory.
    """
    global EXAMPLE_SITE_DIR
    fileDir = os.path.dirname(os.path.abspath(__file__))
    full_example_path = os.path.join(fileDir, "..", EXAMPLE_SITE_DIR)
    for fileOrDir in os.listdir(full_example_path):
        fullPath = os.path.join(full_example_path, fileOrDir)
        if os.path.isfile(fullPath):
            shutil.copy2(fullPath, fileOrDir)
        elif os.path.isdir(fullPath):
            shutil.copytree(fullPath, fileOrDir)
    if not quiet:
        print("Site initialized successfully.")


@runCli.command()
@click.option("--quiet", help="Omit standard output.", type=click.BOOL, default=False)
def build(quiet):
    """ Builds the site at the current working directory.
    """
    buildSite()

    if not quiet:
        print("Finished building successfully.")


@runCli.command()
@click.option("--port", help="Port to serve from", type=click.INT, default=8000)
def serve(port):
    """ Serve the current build of the site at the current working directory
        from localhost.
    """
    global CONFIG_FILE_PATH
    with open(CONFIG_FILE_PATH) as f:
        config = toml.loads(f.read())
    os.chdir(config["build"]["buildDirectory"])
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving website at http://localhost:{port}")
        httpd.serve_forever()
