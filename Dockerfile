FROM gcr.io/broad-getzlab-workflows/base_image:v0.0.5

WORKDIR /build

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.12-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda
     
RUN /opt/conda/bin/conda create -y -n sgz_env python=2.7

# install dependencies
RUN pip install sortedcontainers
ARG cache_invalidate=10


WORKDIR /app
# ENV PATH=$PATH:/app
COPY requirements.txt /app
ENV PATH=/opt/conda/envs/sgz_env/bin:$PATH 
RUN pip install -r requirements.txt
RUN pip uninstall -y pip

# install SGZ
COPY fmiSGZ.py ./fmiSGZ.py
COPY convert_ascat2sgz.py ./convert_ascat2sgz.py
COPY format_maf2sgz.py ./format_maf2sgz.py
