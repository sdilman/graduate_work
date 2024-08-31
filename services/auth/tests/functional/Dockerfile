# Base stage for docker environment setup
FROM python-base:0.1.0 AS base

# Install project dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache-dir ".[test, test-functional]"

ARG USERNAME=auth-tests-functional
ARG TESTS_DIR=/tests/functional

# Copy application code
COPY ./src ./
COPY ."$TESTS_DIR"/src ./tests

# Create non-root user and group
RUN chmod +x ./tests/entrypoint.sh && \
    ./useradd.sh "${GID}" "${UID}" "${USERNAME}" "${BASE_PATH}"

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./tests/entrypoint.sh"]
