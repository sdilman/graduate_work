FROM python:3.12-bullseye

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/app

COPY deploy-test-integration/requirements.app.txt requirements.txt

RUN apt update && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY ./src ./src

RUN chmod +x ./src/entrypoint.sh

ENTRYPOINT ["sh", "src/entrypoint.sh"]