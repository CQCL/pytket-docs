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

Now the built html pages will appear in the local `manual/build` directory.

The manual contains many `jupyter-execute::` directives that run python code when the html is built. The manual build is also run on CI whenever changes are pushed to the pytket repository. If there is are any code snippets that give errors or warnings then the CI build will fail.

If you are making changes to the manual then it is recommended to build the manual locally check the built html pages. If there are no issues then you can commit your change to a local branch and make a pull request.