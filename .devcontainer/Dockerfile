FROM python:3.11.4-slim-bullseye

ENV LANG=C.UTF-8

# Grant ROOT access
USER root

# Install packages and dependencies
RUN apt update && \
    apt install -y --no-install-recommends \
    git \
    ca-certificates \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev

# Set working directory
WORKDIR /opt/app

# Copy files
COPY install_dependencies.sh .
COPY dev-requirements.txt .

# Install dependencies
RUN bash ./install_dependencies.sh ./dev-requirements.txt && \
    rm ./install_dependencies.sh ./dev-requirements.txt
