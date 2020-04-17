#! /usr/bin/env python

import os
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown
from markdown_katex import KatexExtension
import toml

from .admonition import AdmonitionExtension


def read_pages(render_vars, md):
    for typ, info in render_vars["files"].items():
        render_vars[typ] = {}
        if typ == "pages":
            if "files" in info:
                for path in info["files"]:
                    data = load_page(path, md)
                    slug = os.path.splitext(os.path.basename(path))[0]
                    render_vars[typ][slug] = data
            if "directories" in info:
                for path in info["directories"]:
                    dir_files = []
                    for thing in os.listdir(path):
                        if os.path.isfile(os.path.join(path, thing)):
                            data = load_page(os.path.join(path, thing), md)
                            dir_files.append(data)
                    if "sort_by" in info:
                        dir_files.sort(key=lambda x: x[info["sort_by"]])
                    elif "sort_by_reverse" in info:
                        dir_files.sort(
                            key=lambda x: x[info["sort_by_reverse"]], reverse=True
                        )
                    render_vars[typ][path] = dir_files
        else:
            if "files" in info:
                for path in info["files"]:
                    render_vars[typ][path] = path
            if "directories" in info:
                for path in info["directories"]:
                    dir_files = []
                    for thing in os.listdir(path):
                        if os.path.isfile(os.path.join(path, thing)):
                            dir_files.append(os.path.join(path, thing))
                    render_vars[path] = dir_files


def load_page(path, md):
    with open(path) as f:
        body = f.read()
    html = md.convert(body)

    def delistify(p):
        if p[1][0] == "" and len(p[1]) > 1:
            return (p[0], p[1][1:])
        else:
            return (p[0], p[1][0])

    meta = dict(map(delistify, md.Meta.items()))
    if not "slug" in meta:
        meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["url"] = os.path.splitext(path)[0] + ".html"
    if "content" in meta:
        raise KeyError  # TODO improve error handling
    meta["content"] = html
    return meta


def render_pages(render_vars, template):
    if os.path.exists("output"):
        for f in os.listdir("output"):
            os.remove(f"output/{f}")
    else:
        os.mkdir("output")

    for f in os.listdir("assets"):
        shutil.copy(f"assets/{f}", f"output/{f}")

    rendered = template.render(
        {**render_vars, "page": render_vars["pages"]["index"], "is_home": True}
    )
    with open("output/index.html", "w") as f:
        f.write(rendered)

    for post in render_vars["pages"]["posts"]:
        rendered = template.render({**render_vars, "page": post, "is_home": False})
        slug = post["slug"]
        with open(f"output/{slug}.html", "w") as f:
            f.write(rendered)


def render_pages2(render_vars, template):
    if os.path.exists("output"):
        for f in os.listdir("output"):
            os.remove(f"output/{f}")
    else:
        os.mkdir("output")

    for f in os.listdir("assets"):
        shutil.copy(f"assets/{f}", f"output/{f}")

    rendered = template.render(
        {**render_vars, "page": render_vars["pages"]["index"], "is_home": True}
    )
    with open("output/index.html", "w") as f:
        f.write(rendered)

    for post in render_vars["pages"]["posts"]:
        rendered = template.render({**render_vars, "page": post, "is_home": False})
        slug = post["slug"]
        with open(f"output/{slug}.html", "w") as f:
            f.write(rendered)


def compile():
    # Load templates
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("page.html")

    # load vars
    with open("data.toml") as f:
        render_vars = toml.loads(f.read())

    # init markdown system
    md = markdown.Markdown(
        extensions=[
            "meta",
            "fenced_code",
            "tables",
            "codehilite",
            "smarty",
            "sane_lists",
            AdmonitionExtension(),
            KatexExtension(),
        ]
    )

    read_pages(render_vars, md)

    render_pages(render_vars, template)

    print("Build successful!")
