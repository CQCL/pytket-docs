# TKET Developer Blog

## How it works

The TKET blog is currently built using [ablog](https://ablog.readthedocs.io/en/stable/) Sphinx extension.

The source files for the blog posts are in the blog/posts directory. The blog posts can be written in both markdown or reStructuredText and are converted to html pages using the [MyST-parser](https://github.com/executablebooks/MyST-Parser). 

The theme used is the [pydata sphinx theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html). This is the parent theme of the [sphinx book theme](https://sphinx-book-theme.readthedocs.io/en/stable/) which is used for the pytket docs.

The blog is built as part of the docs deployment to github pages in the [core Dockerfile](https://github.com/CQCL-DEV/tket-site/blob/main/core_build/Dockerfile).

## Building the blog locally

After cloning the tket-site repository, navigate to the blog directory and install the required python packages into your local environment.

```shell
pip install -r requirements.txt
```

Now build the html 

```shell
ablog build
```

The built pages will now be in the `_website` folder. 

We can now serve the html.

```shell
ablog serve
```

Finally, we can clear the local build.

```shell
ablog clean
```
 This deletes the `_website` folder.