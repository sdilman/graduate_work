# Base stage for docker environment setup
FROM python-base:0.1.0 AS base

# Install project dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache-dir ".[test, test-integration]"

ARG USERNAME=billing-tests-integration
ARG TESTS_DIR=/tests/integration

# Copy application code
COPY ."$TESTS_DIR"/src ./tests

# Create non-root user and group
RUN ./useradd.sh "${GID}" "${UID}" "${USERNAME}" "${BASE_PATH}" && \
    chmod +x ./tests/entrypoint.sh

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./tests/entrypoint.sh"]
