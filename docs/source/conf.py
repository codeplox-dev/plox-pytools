# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from __future__ import annotations

import sys
import os


project = "plox-tools"
copyright = "2024, codeplox-dev"
author = "codeplox-dev"

highlight_language = "python3"

toc_object_entries = False

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "myst_parser",
    "python_docs_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

typehints_fully_qualified = False
always_use_bars_union = True
autoapi_own_page_level = "module"
#autodoc_default_options = {"show-inheritance": True, "members": True}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True

autoapi_add_toctree_entry = True
autoapi_options = [
    "members",
    "show-inheritance",
    "undoc-members",
    "show-module-summary",
]
autoapi_dirs = ["../../plox"]
autoapi_root = "api"
#autoapi_member_order = "groupwise"
autoapi_member_order = "alphabetical"
autoapi_python_use_implicit_namespaces = True
autoapi_template_dir = "_templates/autoapi"

suppress_warnings = ["myst.header"]

napoleon_attr_annotations = True
napoleon_preprocess_types = True
napoleon_use_rtype = True
napoleon_google_docstring = True
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_param = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
        "python": ("https://docs.python.org/3.12", None),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "python_docs_theme"
html_sidebars = {
   "**": ["globaltoc.html", "sourcelink.html", "searchbox.html"],
   "using/windows": ["windows-sidebar.html", "searchbox.html"],
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

nitpicky = True

sys.path.append(os.path.join(os.path.dirname(__name__), ".."))

nitpick_ignore = {
    ("py:class", "_T"),
    ("py:class", "TupleVal"),
    ("py:class", "plox.tools.files.FilePath")
}

def skip_submodules(app, what, name, obj, skip, options):
    if what == "data" and any(x in name for x in {"logger", "TupleVal"}):
        skip = True
    return skip

def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_submodules)

