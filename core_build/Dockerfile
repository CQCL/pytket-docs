# Build the tket-landing page, manual, notebook examples and blog

### BUILD LANDING PAGE
FROM node:16-alpine AS landing_builder
RUN mkdir -p /usr/src
WORKDIR /usr/src
COPY ./landing_page ./landing_page
WORKDIR /usr/src/landing_page
RUN npm ci
RUN npm run build

### Create docs base stage.
FROM ubuntu:22.04 AS docs_base
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN apt-get update
RUN apt-get install git -y
RUN apt-get install python3-pip -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10
RUN apt-get install graphviz -y
RUN python -m pip install -U pip wheel

### BUILD PYTKET API DOCS
FROM docs_base AS pytket_api_docs_builder
RUN python -m pip install -U pytket
RUN git clone --branch docmain https://github.com/CQCL/tket.git --depth 1
WORKDIR /usr/src/tket
RUN python -m pip install -r ./pytket/docs/requirements.txt
RUN .github/workflows/build-docs

### BUILD PYTKET USER MANUAL 
FROM docs_base AS pytket_manual_builder
RUN git clone https://github.com/CQCL/pytket.git --depth 1
WORKDIR /usr/src/pytket
COPY core_build/manual_docs_requirements.txt .
RUN python -m pip install -r manual_docs_requirements.txt
RUN python -m pip install -r manual_requirements.txt
WORKDIR /usr/src/pytket/manual
RUN sed "s/REQUIREMENTS/$(sed -e 's/[\&/]/\\&/g' -e 's/$/\\n/' ../manual_requirements.txt | tr -d '\n')/" index-rst-template > index.rst
RUN sphinx-build -W -b html . build

### BUILD PYTKET EXAMPLES WITH JUPYTER BOOK
FROM docs_base AS pytket_example_notebooks_builder
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN git clone https://github.com/CQCL/pytket.git --depth 1
WORKDIR /usr/src/pytket
RUN python -m pip install jupyter-book
WORKDIR /usr/src/pytket/examples
RUN python -m pip install -r example_requirements.txt
RUN jupyter-book build -W -v .

### Build blog pages with ablog
FROM docs_base AS tket-blog_builder
RUN mkdir -p /usr/src/blog
WORKDIR /usr/src/blog
COPY blog/requirements.txt .
RUN python -m pip install -r requirements.txt
COPY blog .
RUN ablog build


### COPY GENERATED FILES FROM EACH BUILD STAGE
FROM scratch
COPY --from=landing_builder /usr/src/landing_page/_build/ .
COPY --from=pytket_api_docs_builder /usr/src/tket/pytket/docs/build/html/ ./api-docs/
COPY --from=pytket_manual_builder usr/src/pytket/manual/build ./user-manual/
COPY --from=pytket_example_notebooks_builder /usr/src/pytket/examples/_build/html/ ./examples/
COPY --from=tket-blog_builder /usr/src/blog/_website ./blog
