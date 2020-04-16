#! /usr/bin/env python

import os
import shutil
import sys

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown
from markdown_katex import KatexExtension
import toml

from . import admonition


def main():
    os.chdir("test-site")
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("page.html")
    with open("data.toml") as f:
        render_vars = toml.loads(f.read())

    md = markdown.Markdown(
        extensions=[
            "meta",
            "fenced_code",
            "tables",
            "codehilite",
            "smarty",
            "sane_lists",
            admonition.AdmonitionExtension(),
            KatexExtension(),
        ]
    )
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
    posts.sort(key=lambda x: x["date"])
    render_vars["posts"] = posts

    for page in render_vars["posts"] + [render_vars["index"]]:
        slug = page["slug"]
        page["url"] = f"{slug}.html"

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

    print("Build successful!")


if __name__ == "__main__":
    main()
