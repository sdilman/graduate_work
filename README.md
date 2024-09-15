# Project Description
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?logo=docker&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)]()
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)]()
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?logo=apache-kafka&logoColor=white)]()
[![NGINX](https://img.shields.io/badge/NGINX-269539?logo=nginx&logoColor=white)]()
[![ngrok](https://img.shields.io/badge/ngrok-1F1E37?logo=ngrok&logoColor=white)]()


This billing microservice is designed for an online cinema platform, providing a seamless and secure way to handle transactions and subscriptions.

## Key Features

- **Order Placement**: Allows users to place orders for content or subscriptions.
- **Idempotency**: Configured to prevent duplicate transactions, ensuring transaction safety.
- **Payment Processing**: Returns a payment link for the selected provider upon order placement (currently supports one provider).
- **Subscription Management**: Offers the option to opt out of automatic subscription renewals.
- **Refund Handling**: Enables users to request and receive refunds.

## Architecture

- **FastAPI**: Serves as the framework for building the RESTful API.
- **Kafka**: Utilized for message brokering and handling asynchronous communication.
- **Workers**: Background processes that read messages from Kafka to perform tasks like order processing, subscription renewals, and sending notifications.

## How to run a project

```bash
make up_all
```
