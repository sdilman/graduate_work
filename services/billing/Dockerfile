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
ENV PYTHONPATH="$BASE_PATH"

# Set work directory
WORKDIR "$BASE_PATH"

# Set the default shell to bash with pipefail option
SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# Install uv
# https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.3.3 /uv /bin/uv

# Install project dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache-dir -r pyproject.toml

ARG USERNAME=billing

# Copy application code
COPY ./src ./

# Create non-root user and group
RUN groupadd -g "${GID}" "${USERNAME}" && \
    useradd -l -m -u "${UID}" -g "${USERNAME}" -s /bin/bash "${USERNAME}" && \
    chown -R "${USERNAME}":"${USERNAME}" "$BASE_PATH" && \
    chmod +x ./entrypoint.sh

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./entrypoint.sh"]
