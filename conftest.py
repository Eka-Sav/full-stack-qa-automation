import uuid
from collections.abc import Callable, Generator

import pytest
from sqlalchemy import text

from api.api_client import APIClient
from api.endpoints import Endpoints
from data.products import PRODUCTS
from database.db_manager import DBManager


@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    with APIClient() as client:
        yield client


@pytest.fixture(scope="function")
def db() -> Generator[DBManager, None, None]:
    with DBManager() as manager:
        yield manager


@pytest.fixture(scope="session", autouse=True)
def clean_db_before_run() -> None:
    with DBManager() as manager:
        for table in ("transactions", "orders", "accounts", "products", "users"):
            manager.session.execute(text(f"DELETE FROM {table}"))
        manager.session.commit()


# users and accounts


def _build_user_data(faker) -> dict:
    return {
        "username": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"{uuid.uuid4().hex[:8]}@{faker.domain_name()}",
        "password": faker.password(length=10),
    }


def _create_user(api_client, user_data: dict) -> dict:
    response = api_client.post(Endpoints.USERS, json=user_data)
    assert response.status_code == 201, f"Failed to create user: {response.text}"
    user = response.json()
    user["password"] = user_data["password"]
    return user


def _get_account(api_client, user_id: int) -> dict:
    response = api_client.get(Endpoints.accounts(user_id))
    assert response.status_code == 200, f"Failed to get account: {response.text}"
    accounts = response.json()
    assert accounts, f"No accounts for user {user_id}"
    return accounts[0]


@pytest.fixture
def user_data(faker) -> dict:
    return _build_user_data(faker)


@pytest.fixture
def created_user(api_client: APIClient, user_data: dict) -> dict:
    return _create_user(api_client, user_data)


@pytest.fixture
def user_account(api_client: APIClient, created_user: dict) -> dict:
    return _get_account(api_client, created_user["id"])


@pytest.fixture
def recipient_data(faker) -> dict:
    return _build_user_data(faker)


@pytest.fixture
def created_recipient(api_client: APIClient, recipient_data: dict) -> dict:
    return _create_user(api_client, recipient_data)


@pytest.fixture
def recipient_account(api_client: APIClient, created_recipient: dict) -> dict:
    return _get_account(api_client, created_recipient["id"])


@pytest.fixture
def auth_token(api_client: APIClient, created_user: dict) -> str:
    response = api_client.post(
        Endpoints.LOGIN,
        json={
            "username": created_user["username"],
            "password": created_user["password"],
        },
    )
    assert response.status_code == 200, f"Failed to log in: {response.text}"
    return response.json()["access_token"]


# products


@pytest.fixture
def product_data(faker) -> dict:
    return {
        "name": faker.word().capitalize() + " Service",
        "description": faker.sentence(),
        "price": round(faker.pyfloat(min_value=1, max_value=1000, right_digits=2), 2),
        "category": faker.random_element(["service", "travel", "goods"]),
    }


@pytest.fixture
def created_product(api_client: APIClient, product_data: dict) -> dict:
    response = api_client.post(Endpoints.PRODUCTS, json=product_data)
    assert response.status_code == 201, f"Failed to create product: {response.text}"
    return response.json()


@pytest.fixture
def created_products(api_client: APIClient) -> Generator[list[dict], None, None]:
    result = []
    for product in PRODUCTS:
        response = api_client.post(Endpoints.PRODUCTS, json=product)
        assert response.status_code == 201, f"Failed to create products: {response.text}"
        result.append(response.json())
    yield result
    for created in result:
        api_client.delete(Endpoints.product(created["id"]))


@pytest.fixture
def product_factory(api_client: APIClient, faker) -> Callable[..., dict]:
    def _create(category: str | None = None, price: float | int | None = None, name: str | None = None) -> dict:
        response = api_client.post(
            Endpoints.PRODUCTS,
            json={
                "name": name if name is not None else faker.word().capitalize(),
                "description": faker.sentence(),
                "price": price
                if price is not None
                else round(faker.pyfloat(min_value=1, max_value=1000, right_digits=2), 2),
                "category": category or faker.random_element(["service", "travel", "goods"]),
            },
        )
        assert response.status_code == 201, f"Failed to create products: {response.text}"
        return response.json()

    return _create


@pytest.fixture
def deactivated_product(api_client: APIClient, created_product: dict) -> dict:
    response = api_client.delete(Endpoints.product(created_product["id"]))
    assert response.status_code == 204, f"Failed to deactivate product: {response.text}"
    return created_product


# orders


@pytest.fixture
def order_data(created_user: dict, created_product: dict) -> dict:
    return {
        "user_id": created_user["id"],
        "product_id": created_product["id"],
        "quantity": 2,
    }


@pytest.fixture
def created_order(api_client: APIClient, order_data: dict) -> dict:
    response = api_client.post(Endpoints.ORDERS, json=order_data)
    assert response.status_code == 201, f"Failed to create order: {response.text}"
    return response.json()


@pytest.fixture
def cancelled_order(api_client: APIClient, created_order: dict) -> dict:
    response = api_client.patch(Endpoints.order_cancel(created_order["id"]))
    assert response.status_code == 200, f"Failed to cancel order: {response.text}"
    return {**created_order, **response.json()}


@pytest.fixture
def confirmed_order(api_client: APIClient, created_order: dict) -> dict:
    response = api_client.patch(Endpoints.order_confirm(created_order["id"]))
    assert response.status_code == 200, f"Failed to confirm order: {response.text}"
    return {**created_order, **response.json()}


@pytest.fixture
def paid_order(api_client: APIClient, confirmed_order: dict, created_transaction_deposit: dict) -> dict:
    response = api_client.post(Endpoints.order_pay(confirmed_order["id"]))
    assert response.status_code == 200, f"Failed to pay order: {response.text}"
    return {**confirmed_order, **response.json()}


# transactions


@pytest.fixture
def transaction_deposit_data(user_account: dict, faker) -> dict:
    return {
        "account_id": user_account["id"],
        "amount": 10000,
        "transaction_type": "deposit",
        "description": faker.sentence(),
    }


@pytest.fixture
def created_transaction_deposit(api_client: APIClient, transaction_deposit_data: dict) -> dict:
    response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
    assert response.status_code == 201, f"Failed to create deposit: {response.text}"
    return response.json()


@pytest.fixture
def transfer_data(created_transaction_deposit: dict, user_account: dict, recipient_account: dict, faker) -> dict:
    return {
        "from_account_id": user_account["id"],
        "to_account_id": recipient_account["id"],
        "amount": 10.00,
        "description": faker.sentence(),
    }


@pytest.fixture
def created_transfer(api_client: APIClient, transfer_data: dict) -> dict:
    response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
    assert response.status_code == 201, f"Failed to create transfer: {response.text}"
    return response.json()

