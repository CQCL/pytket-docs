# Contributing to pytket

Pull requests are welcome. To make a PR, first fork the repo, make your proposed
changes on the `main` branch, and open a PR from your fork. If it passes
the checks and is accepted after review, it will be merged in.
If there are any changes to the manual part of the repo the
manual needs to be rebuilt locally.

## pre-commit

We use [pre-commit](https://pre-commit.com/#automatically-enabling-pre-commit-on-repositories) to catch formatting and other issues before committing to the repo. If you have installed the required packages with `pip install -r requirements.txt`, then you should already have `pre-commit` available.

To install the hooks, simply run `pre-commit install`. After that, the checks will be run automatically whenever you do a `git commit`.

## Formatting

All Python code should be formatted using
[black](https://black.readthedocs.io/en/stable/), with default options. This is
checked on the CI. This is done automatically if you have installed the `pre-commit` hooks as described earlier. You can also run the checks manually on any staged files with `pre-commit run --all-files black`.
