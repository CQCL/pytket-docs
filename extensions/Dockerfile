# Builds the documentation for a particular pytket extension.
ARG EXTENSION_NAME

FROM ubuntu:22.04 AS docs_base
RUN mkdir -p /usr/src
WORKDIR /usr/src
RUN apt-get update
# RUN apt-get install wget -y
# RUN wget https://packages.microsoft.com/config/ubuntu/22.10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
# RUN dpkg -i packages-microsoft-prod.deb
# RUN rm packages-microsoft-prod.deb
# RUN apt-get update
# RUN apt-get install -y dotnet-sdk-7.0
# RUN dotnet tool install --global Microsoft.Quantum.IQSharp
# RUN dotnet iqsharp install --user
RUN apt-get install git -y
RUN apt-get install python3-pip -y
RUN apt-get install python3.11 -y
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 11
RUN python -m pip install -U pip wheel
COPY extensions/requirements.txt .
RUN python -m pip install -r requirements.txt


FROM docs_base AS extensions_builder
ARG EXTENSION_NAME
RUN python -m pip install -U $EXTENSION_NAME
RUN git clone --branch main https://github.com/CQCL/$EXTENSION_NAME.git --depth 1
WORKDIR /usr/src/$EXTENSION_NAME
RUN mkdir .github/workflows/docs/extensions
WORKDIR /usr/src/$EXTENSION_NAME/docs/
RUN rm -d -r _static
# Make _static directory for the custom.css file
RUN mkdir -p _static
COPY extensions/_static ./_static
WORKDIR /usr/src/$EXTENSION_NAME/.github/workflows/docs/
# Remove legacy conf.py with old theme settings
RUN rm conf.py 
# Copy in the pytket-quantinuum conf.py from tket-site repository
COPY extensions/conf.py .
# Replace pytket-quantinnum with extension name
RUN sed -i "s/pytket-quantinuum/"$EXTENSION_NAME"/" conf.py
RUN ./build-docs -d ./extensions/

FROM scratch
ARG EXTENSION_NAME
COPY --from=extensions_builder /usr/src/$EXTENSION_NAME/.github/workflows/docs/extensions/ ./
