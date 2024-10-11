# User Guide Documentation (Manual + Example Notebooks)

## Building the Docs

The manual and examples are both built as a single sphinx site with shared dependencies. The [Quantinuum-sphinx](https://github.com/CQCL/quantinuum-sphinx) templates are used for styling.

The docs can be built locally by following these steps

1. First clone this repository including the [pytket-docs-theming](https://github.com/CQCL/pytket-docs-theming) submodule

```shell
git clone git@github.com:CQCL/pytket-docs.git --recurse-submodules
```

If you use `git pull` inside the `docs/pytket-docs-theming` directory, you should be using the latest version of the theming.

2. Next, install the dependencies using poetry

```shell
poetry install
```

3. Finally, run the `build-docs.sh` script from the root directory.

```
poetry run ./build-docs.sh
```

This will execute the jupyter cells in the manual and example notebooks and show the outputs of most cells.

Some notebooks are currently excluded from execution at the moment. These notebooks are listed [here](https://github.com/CQCL/pytket-docs/blob/main/docs/conf.py#L46).

