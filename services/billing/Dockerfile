FROM python-base:0.1.0 AS base

# Install project dependencies
COPY pyproject.toml .
RUN uv pip install --system --no-cache-dir -r pyproject.toml

ARG USERNAME=billing

# Copy application code
COPY ./src ./

# Create non-root user and group
RUN chmod +x ./entrypoint.sh ./workers_entrypoint.sh && \
    ./useradd.sh "${GID}" "${UID}" "${USERNAME}" "${BASE_PATH}"

# Switch to non-root user
USER "${USERNAME}"

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./entrypoint.sh"]
