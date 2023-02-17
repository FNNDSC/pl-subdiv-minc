FROM docker.io/fnndsc/mni-conda-base:civet2.1.1-python3.10.6

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="Subdivide Masks" \
      org.opencontainers.image.description="A ChRIS plugin wrapper around mincresample for increasing the resolution of binary images."

WORKDIR /usr/local/src/pl-subdiv-minc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ARG extras_require=none
RUN pip install ".[${extras_require}]"

CMD ["subdiv_mask", "--help"]
