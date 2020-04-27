=====================
Static Site Generator
=====================

What is this?
=============

A homebrewed static website generator, which I built because I was bored during COVID-19 social isolation.

.. code::

    Usage: ssg [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    build  Builds the site at the current working directory.
    init   Initialize the example site at the current working directory.
    serve  Serve the current build of the site at the current working...

Site design
===========

Call `ssg init` to initialize the sample website in the current directory.

config.toml
-----------

The config file `config.toml` defines a lot of important stuff about the website.

.. code:: toml

    [site]
    title = "Sample Blog"
    subtitle = "Just Boilerplate"
    description = "Just a sample blog"

    [build]
    buildDirectory = "output"

    [templates]
    directories = ["templates"]

    [pages.posts]
    directories = ["posts"]
    sortByDate = true
    sortReverse = true

    [pages.general]
    files = ["index.md"]

    [assets]
    directories = ["assets"]

The stuff under `site` is pretty self-descriptive.
Note that it will only be used as dictated by the templates, so you ultimately have control over how it's used.

The parameter `buildDirectory` is the relative path of the directory where the site will be built.

The tables `templates`, `pages.<category>`, and `assets` all have a common format:
they have an optional field `files` and an optional field `directories`.
`files` is a list of loose files that should be included in this group
and `directories` is a list of directories whose files will be included in this group.
Note that directories listed under `directories` are not searched recursively.

Note that `posts` and `general` are not hard-coded `page.<category>` names; any name can be used.
These categories are relevant for templating purposes.

`sortByDate` and `sortReverse` are two parameters available in `pages` categories which describe
how the categories will be sorted when they are iterated through in templates.

Article writing
---------------

Articles are written in markdown.
At the top of the document is some TOML front matter describing data about the post.

.. code: markdown

    ---
    title = "Sample Post 1"
    date = 2020-04-16
    description = "The first of my sample posts"
    template = "page.html"
    ---

    This is the first sample post.

    Look, it has **fancy** *words* in it!
    And "smart" quotes, and nice --- dashes.
    And $`x + y = z`$ fancy math too.

    !!! is-danger "Info"
        Visit [the second sample post.](sample2.html)

    ```math
    \lim_{n \to \infty} \sum_{i = 0}^n = \infty
    ```
The post itself is written in extended markdown, which includes LaTeX-based math and admonitions.
Admonitions are designed to be compatible with the Bulma CSS framework, but custom CSS can be written for them.

Templates
---------

Templates are HTML Jinja2 documents.
Some examples of values available to templates:

- `{{ site.title }}` is the site title as listed in `config.toml`
    * Other `site` members are similarly available
- `{{ pages.index }}` will retrieve the relative url of a page with the filename `index.md`. Other page parameters include:
    * `title`: from `config.toml`
    * `date`: from `config.toml`
    * `description`: from `config.toml`
    * `content`: the fully-rendered HTML contents of the page
    * `group`: the category (as in `posts` or `general` in the example) that the page falls into
- `{{ currentPage.url }}` similarly gives the url (or whatever) of the page currently being rendered
- `{% for post in pages.posts %} ... {% endfor %}` will loop through all the pages in the category `posts` in the order they were sorted


TODO:

- Packaging tools
- Better error handling
    * Fail helpfully out of missing configs
    * Fail helpfully on Jinja error
- Default values for config
- RSS? Use a different tool for that maybe
