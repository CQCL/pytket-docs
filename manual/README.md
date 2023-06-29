# The pytket User Manual

The manual is built from several reStructuredText (.rst) files in the manual directory.

The manual can be built locally as follows.

First clone the pytket repository

```shell
git clone git@github.com:CQCL/pytket.git
```

It is recommended to set up a virtual environment in the pytket repository to manage dependencies.

Once the virtual environment is set up we can run the `build-manual` script from the pytket directory which installs the necessary python packages and builds the html pages.

```shell
./build-manual
```

Now the built html pages will appear in the local `docs/manual` directory. Its recommended to view the html pages locally after making changes to the source files.

If you want to make changes to the manual then you can commit changes to the source files on a local branch. Note that due to a current limitation of the manual build you will need to also commit changes to the built html file.

For example if edits were made to `manual_backend.rst`. The html file `manual_backend.html` will also need to be added to the pull request as well.

Note that the entire `docs/manual` directory gets deployed whenever a pull request is merged. The changes made in the pull request should show up in the github pages site as soon as the workflow run finishes.