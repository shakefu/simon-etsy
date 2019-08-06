# Stage for making a Ubuntu compatible executable
FROM ubuntu:18.04 AS build

WORKDIR /usr/src/app

# Make sure we never get asked a question
ENV DEBIAN_FRONTEND=noninteractive

RUN \
    # Update, quietly
    apt-get update -yqq  && \
    # Install Python 3
    apt-get install -yqq python3 python3-pip && \
    # Remove artifacts, cache, other junk
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make python3 and pip3 the defaults
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10 && \
    update-alternatives --install /usr/local/bin/python python /usr/bin/python3.6 10 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

# Uncomment this to sanity check we're getting Python 3.6 or later
# RUN python3 --version

# Install builder
RUN pip install pyinstaller

# Copy in the app code
COPY setup.py setup.py
COPY simon_etsy/ simon_etsy/

# Install dependencies
RUN pip install  .

# Make nltk directories for linking
RUN mkdir -p /usr/nltk_data /usr/share/nltk_data /usr/lib/nltk_data \
    /usr/local/share/nltk_data /usr/local/lib/nltk_data /root/nltk_data
# Install nltk minimal files
RUN python -m nltk.downloader -d /usr/share/nltk_data punkt averaged_perceptron_tagger

# Building executable
RUN pyinstaller --onefile simon_etsy/__main__.py --name simon-etsy

# Stage for executable container
FROM python:3.6 AS final

# Copy artifacts from previous build
COPY --from=build /usr/src/app/dist/simon-etsy /usr/local/bin/simon-etsy
# COPY --from=build /root/nltk_data/ /root/nltk_data/

# Use our command for container runtime
ENTRYPOINT ["/usr/local/bin/simon-etsy"]
