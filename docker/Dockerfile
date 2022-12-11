# Pull base image
FROM python:3.8.13-alpine3.16

# Install tools

RUN apk add --no-cache git postgresql-dev gcc libc-dev
RUN apk add --no-cache gcc g++ make libffi-dev python3-dev build-base freetype-dev
RUN apk add py3-pip py3-pillow py3-cffi py3-brotli gcc musl-dev python3-dev pango

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Clone git repo

RUN git clone https://github.com/PGPI-G3-06/Acme-NFT.git

# Set work directory

WORKDIR /Acme-NFT/acme_nft

# Install dependencies

RUN pip3 install -U pip
RUN pip3 install gunicorn
RUN pip3 install ipdb
RUN pip3 install ipython
RUN pip3 install ez_setup
RUN pip3 install --upgrade setuptools
RUN pip3 install reportlab --use-deprecated=legacy-resolver
RUN pip3 install -r requirements.txt

# Create static files

RUN python manage.py collectstatic --noinput