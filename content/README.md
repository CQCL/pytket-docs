# Docs Prototype

## Summary of changes

* Manual, blog and examples are now one sphinx project (Using [pydata](https://pydata-sphinx-theme.readthedocs.io/en/stable/) but flexible)
* Navbar across docs pages (Using pydata builtin navbar but could use custom)
* Use poetry for dependency management
* Use sphinx-gallery for displaying examples. This uses python scripts as source avoiding code duplication and source control issues from using jupyter notebooks source


## Building the docs locally

Clone the pytket repo if you haven't already

```shell
git clone git@github.com:CQCL/pytket.git
```

Change to the `prototype/docs_refactor` branch

```shell
git checkout prototype/docs_refactor
```

Now install dependencies. This requires [poetry](https://python-poetry.org/docs/#installation) to be installed on your system.

```shell
poetry install
```
Once dependencies are installed, activate poetry shell and run the sphinx build command.

```shell
poetry shell
sphinx-build -M html content content/build
```

The html pages will show up in the `content/build/html` directory.

```shell
open content/build/html/index.html
```
