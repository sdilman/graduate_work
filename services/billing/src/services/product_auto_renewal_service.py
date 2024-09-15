from __future__ import annotations

from typing import cast

import asyncio

from base64 import b64encode
from collections import defaultdict
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

import httpx

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from core.constraints import OrderStatus, TransactionStatus, TransactionType
from core.logger import get_logger
from core.settings import settings
from models.pg import Order, PaymentMethod, Transaction, UserProduct
from schemas.entity import OrderSchema
from services.order_service import OrderService

logger = get_logger(__name__)


class ProductRenewalService:
    def __init__(self, session: AsyncSession, order_service: OrderService):
        self._session = session
        self._order_service = order_service

    async def _get_products_for_renewal(self) -> dict[str, list[UserProduct]]:
        stmt = select(UserProduct).where(
            and_(UserProduct.renewal_enabled == True, UserProduct.active_till <= datetime.now())  # noqa: E712
        )
        result = await self._session.execute(stmt)
        user_products = result.scalars()
        products_per_users = defaultdict(list)
        for product in user_products:
            products_per_users[product.user_id].append(product)
        return products_per_users

    async def _get_users_with_pending_auto_orders(self) -> set[str]:
        # todo: add this field to model
        # todo: add Order.type == OrderType.AUTO_CREATED in and_

        stmt = select(Order.user_id).where(and_(Order.status == OrderStatus.PENDING)).distinct()

        result = await self._session.execute(stmt)
        return set(result.scalars())

    async def _create_orders(self, products_per_users: dict[str, list[UserProduct]]) -> dict[str, Order]:
        orders_per_users = {}
        for user_id, products in products_per_users.items():
            order = await self._order_service.create_order(
                OrderSchema(user_id=user_id, products_id=[str(p.product_id) for p in products])
            )
            orders_per_users[user_id] = order
        return orders_per_users

    async def _create_auto_renewal_transactions(self, orders: list[Order]) -> dict[str, Transaction]:
        transactions_per_orders = {}
        for order in orders:
            transactions_per_orders[order.id] = Transaction(
                order_id=order.id,
                type=TransactionType.PAYMENT,
                status=TransactionStatus.PENDING,
                currency=order.currency,
                amount=order.total_amount,
            )
        self._session.add_all(transactions_per_orders.values())
        return transactions_per_orders

    async def _get_available_users_payment_methods(self, user_ids: list[str]) -> dict[str, list[str]]:
        stmt = select(PaymentMethod).where(and_(PaymentMethod.user_id.in_(user_ids), PaymentMethod.is_active == True))  # noqa: E712
        results = await self._session.execute(stmt)
        results = results.scalars()
        payment_methods_per_users = defaultdict(list)
        for p in results:
            payment_methods_per_users[p.user_id].append(p.payment_token)
        return payment_methods_per_users

    async def _create_auto_renewal_payment_object(
        self, client: httpx.AsyncClient, payment_method_id: str, transaction: Transaction
    ) -> bool:
        idempotence_key = str(uuid4())
        auth = b64encode(f"{settings.payment.account_id}:{settings.payment.secret_key}".encode()).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth}",
            "Idempotence-Key": idempotence_key,
            "Content-Type": "application/json",
        }
        payment_data = {
            "amount": {"value": str(transaction.amount), "currency": str(transaction.currency.value).upper()},
            "payment_method_id": payment_method_id,
            "capture": True,
            "description": f"Automatic payment for order №{transaction.order_id}",
            "metadata": {"transaction_id": transaction.id},
        }
        try:
            response = await client.post("https://api.yookassa.ru/v3/payments", headers=headers, json=payment_data)
        except Exception as e:
            return False

        return cast(bool, response.status_code == HTTPStatus.OK)

    async def _create_auto_renewal_payment_objects(
        self, transactions: list[Transaction], payment_methods_per_transactions: dict[str, list[str]]
    ) -> None:
        tasks = []
        async with httpx.AsyncClient() as client:
            for transaction in transactions:
                payment_methods = payment_methods_per_transactions.get(transaction.id)
                if payment_methods:
                    task = asyncio.create_task(
                        self._create_auto_renewal_payment_object(client, payment_methods[0], transaction)
                    )
                    tasks.append(task)
            await asyncio.gather(*tasks)

    # TODO: add transaction here
    async def run_renewal(self) -> None:
        products_per_users = await self._get_products_for_renewal()
        user_ids_to_exclude = await self._get_users_with_pending_auto_orders()
        products_per_users = {k: v for k, v in products_per_users.items() if k not in user_ids_to_exclude}

        orders_per_users = await self._create_orders(products_per_users)
        orders = list(orders_per_users.values())
        transactions_per_orders = await self._create_auto_renewal_transactions(orders)

        users = list(orders_per_users.keys())
        payment_methods_per_users = await self._get_available_users_payment_methods(users)

        payment_methods_per_transactions = {
            transactions_per_orders[orders_per_users[user_id].id].id: payment_methods
            for user_id, payment_methods in payment_methods_per_users.items()
        }

        transactions = list(transactions_per_orders.values())
        await self._session.commit()

        await self._create_auto_renewal_payment_objects(transactions, payment_methods_per_transactions)
