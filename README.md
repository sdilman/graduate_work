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

## How to run a project

```bash
make up_all
```

## Key Features

- **Order Placement**: Allows users to place orders for content or subscriptions.
- **Idempotency**: Configured to prevent duplicate transactions, ensuring transaction safety.
- **Payment Processing**: Returns a payment link for the selected provider upon order placement (currently supports one provider).
- **Subscription Management**: Offers the option to opt out of automatic subscription renewals.
- **Refund Handling**: Enables users to request and receive refunds.

## Architecture

- **FastAPI**: This is the framework we use for the API. The API mainly forwards requests to Kafka with minimal processing. All the business logic happens in the background workers.
- **Kafka**: A message broker that handles communication between the API and the workers. The API sends requests to Kafka, and the workers pick up those messages to process them.
- **Workers**: These are background processes that handle tasks like order processing, subscription renewals, and notifications. They do the main work and can easily scale horizontally to handle more tasks.
- **Payment Provider**: The service supports multiple payment providers. The workers request payment links from the providers, making it easy to switch or add new providers.
- **Scalability**: Both Kafka and the workers can scale horizontally. This means the system can grow as needed by adding more Kafka brokers or workers.


![Billing Service Diagram](https://www.plantuml.com/plantuml/png/RL9BYzim4BxFhnXyQWyBfT0Uo-xs0KkNOXfA3s4f4tbYYyYIAerJGjd_NkknZaFZWppVzyrRker2GQRHG3newodGY4PRbfDdT446jnAK6xspR6KZ9yCOM0dPtl1L5qzAsnxVlrcfrdLyLUY3c_o37JXe8QkufQvBJc_VWU6ze3WCkXy4EvsgQcS1I8aBsFo871gaYDDi06o_16U5RVUKk7q50BDoDyc0T-r3LcW6e9mn9Lt4fgNJo5Qm3UweEmunP_M5_ULVM0I0PN9ixhKngTCDXwDMd6DsbViBcBzjTJeNzpfBvsELyHC9xIWoFjAfZjRDr98D4omUJUkYz85ZyTfTyVZEdOxuaTHGUbF9odxFv-eNU_ZfmY7DQPRoVpAp9ByqVayypNK-7zFkxgU8hxxI_a2lS-GXcV1yiR7DvBqBKZTMUu-LB4Dk7rtVhxRwLDXlJlHUAqgDBbBAdguURsu-dE_xnSXilGyWhnEkNLMKTmNfo6Xc8Ua5rSdBRnLRYHg-nly_6AZbirhdN7FbATwoxQRH_0C0)
