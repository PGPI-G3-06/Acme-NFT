# Pull base image
FROM python:3.8.13-alpine3.16

# Install tools

RUN apk add --no-cache git postgresql-dev gcc libc-dev
RUN apk add --no-cache gcc g++ make libffi-dev python3-dev build-base
RUN apk add py3-pip py3-pillow py3-cffi py3-brotli gcc musl-dev python3-dev pango
RUN apt-get install libfreetype-dev libfreetype6 libfreetype6-dev

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Clone git repo

RUN git clone https://github.com/PGPI-G3-06/Acme-NFT.git

# Set work directory

WORKDIR /Acme-NFT/acme_nft

# Install dependencies

RUN pip install -U pip
RUN pip install -r requirements.txt

# Create static files

RUN python manage.py collectstatic --noinput