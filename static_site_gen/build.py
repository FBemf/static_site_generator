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
        render_vars[typ] = []
        if typ == "pages":
            for path in info["files"]:
                data = load_page(path, md)
                render_vars[typ].append(data)
            for path in info["directories"]:
                for thing in os.listdir(path):
                    if os.isfile(thing):
                        data = load_page(os.path.join(path, thing), md)
                        render_vars[typ].append(data)
            if "sort_by" in info:
                render_vars[typ].sort(key=lambda x: x[info["sort_by"]])
            elif "sort_by_reverse" in info:
                render_vars[typ].sort(
                    key=lambda x: x[info["sort_by_reverse"]], reverse=True
                )
        else:
            for path in info["files"]:
                render_vars[typ].append(path)
            for path in info["directories"]:
                for thing in os.listdir(path):
                    if os.isfile(thing):
                        render_vars[typ].append(os.path.join(path, thing))


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
        meta["slug"] = os.path.basename(path)
    if "content" in meta:
        raise KeyError  # TODO improve error handling
    meta["content"] = html
    return meta


def read_pages2(render_vars, md):
    with open(f"index.md") as f:
        text = f.read()
    html = md.convert(text)
    try:
        render_vars["index"] = {
            "title": md.Meta["title"][0],
            "slug": "index",
            "content": html,
        }
    except (KeyError, IndexError) as e:
        print(f"Bad metadata in index.md: {e}")
        sys.exit(1)

    posts = []
    for file in os.listdir("posts"):
        with open(f"posts/{file}") as f:
            text = f.read()
        html = md.convert(text)
        try:
            current_post = {
                "title": md.Meta["title"][0],
                "slug": os.path.splitext(file)[0],
                "date": md.Meta["date"][0],
                "description": md.Meta["description"][0],
                "content": html,
            }
            current_post["description"] = md.convert(md.Meta["description"][0])
            posts.append(current_post)
        except (KeyError, IndexError) as e:
            print(f"Bad metadata in post {file}: {e}")
            sys.exit(1)
    posts.sort(key=lambda x: x["date"], reverse=True)
    render_vars["posts"] = posts

    for page in render_vars["posts"] + [render_vars["index"]]:
        slug = page["slug"]
        page["url"] = f"{slug}.html"


def render_pages(render_vars, template):
    if os.path.exists("output"):
        for f in os.listdir("output"):
            os.remove(f"output/{f}")
    else:
        os.mkdir("output")

    for f in os.listdir("assets"):
        shutil.copy(f"assets/{f}", f"output/{f}")

    rendered = template.render(
        {**render_vars, "page": render_vars["index"], "is_home": True}
    )
    with open("output/index.html", "w") as f:
        f.write(rendered)

    for post in render_vars["posts"]:
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

    read_pages2(render_vars, md)

    render_pages(render_vars, template)

    print("Build successful!")
