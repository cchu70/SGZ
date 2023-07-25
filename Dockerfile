# FROM gcr.io/broad-getzlab-workflows/base_image:v0.0.5
RUN apt-get update && apt-get install -y python2.7

WORKDIR /build

# install dependencies
# RUN pip install sortedcontainers
ARG cache_invalidate=10


WORKDIR /app
ENV PATH=$PATH:/app

# install SGZ
COPY fmiSGZ.py ./fmiSGZ.py

COPY setup.py .
RUN pip install .
