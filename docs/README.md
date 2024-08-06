# User Guide Documentation (Manual + Example Notebooks)

## Building the Docs

The manual and examples are both built as a single sphinx site with shared dependencies.

The docs can be built locally by following these steps

1. First clone this repository

```shell
git@github.com:CQCL/pytket-docs.git
```

2. Next, install the dependencies using poetry

```shell
poetry install
```

3. Finally, run the `build-docs.sh` script

```
./build-docs.sh
```