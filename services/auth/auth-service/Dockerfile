FROM python:3.11-slim AS base

WORKDIR /app
ENV PATH /app/.venv/bin/:$PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir


FROM base AS prod

COPY --from=base /app /app
COPY src ./src
COPY main.py \
    entrypoint.sh \
    alembic.ini \
    migrations.py \
    gunicorn_conf.py ./

RUN chmod +x entrypoint.sh

# Use entrypoint.sh to perform run tasks
ENTRYPOINT ["./entrypoint.sh"]


FROM base AS tests

COPY --from=base /app /app
COPY tests tests
ENV PYTHONPATH /app
RUN chmod 774 ./tests/functional/utils/tests_entrypoint.sh

ENTRYPOINT [ "./tests/functional/utils/tests_entrypoint.sh" ]
