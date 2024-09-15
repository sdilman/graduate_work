# Base stage for docker environment setup
FROM python:3.12-slim-bookworm AS base

# Set environment variables
    # user
ENV GID=1000 \
    UID=1000 \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # path
    BASE_PATH=/opt/app \
    # uv
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Set python path
ENV PYTHONPATH="$BASE_PATH":"$BASE_PATH"/tests

# Set work directory
WORKDIR "$BASE_PATH"

# Set the default shell to bash with pipefail option
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# Copy common files
COPY ./useradd.sh ./useradd.sh
RUN chmod +x ./useradd.sh

# Install uv
# https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.4.10 /uv /bin/uv

# Initialize
CMD ["sleep", "1"]
