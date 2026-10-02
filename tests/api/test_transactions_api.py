"""API tests for /transactions: create deposit, list by account, get by id"""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints

pytestmark = [
    allure.epic("Transactions & Balance"),
    pytest.mark.api,
]


@allure.feature("Deposit")
class TestCreateTransaction:
    @allure.story("Deposit increases account balance")
    @pytest.mark.smoke
    def test_create_transaction_deposit_returns_201(
        self, api_client: APIClient, transaction_deposit_data: dict, created_user: dict
    ) -> None:
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        new_transaction = response.json()
        assert new_transaction is not None
        assert new_transaction["id"] is not None
        assert new_transaction["account_id"] == transaction_deposit_data["account_id"]
        assert new_transaction["amount"] == transaction_deposit_data["amount"]
        assert new_transaction["transaction_type"] == transaction_deposit_data["transaction_type"]
        assert new_transaction["description"] == transaction_deposit_data["description"]
        assert new_transaction["transaction_type"] == "deposit"
        assert new_transaction["direction"] == "in"
        assert new_transaction["created_at"] is not None
        response = api_client.get(Endpoints.accounts_by_account_number(created_user["account_number"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        account = response.json()
        assert account["balance"] == transaction_deposit_data["amount"]

    @allure.story("Deposit increases account balance")
    def test_created_transaction_deposit_response_schema(self, created_transaction_deposit: dict) -> None:
        assert isinstance(created_transaction_deposit["id"], int)
        assert isinstance(created_transaction_deposit["account_id"], int)
        assert isinstance(created_transaction_deposit["amount"], float)
        assert isinstance(created_transaction_deposit["transaction_type"], str)
        assert isinstance(created_transaction_deposit["direction"], str)
        assert isinstance(created_transaction_deposit["description"], str)

    @allure.story("Deposit rejected: account not found")
    @pytest.mark.negative
    def test_create_transaction_deposit_nonexistent_account_id_returns_404(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data["account_id"] = 123123123
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Account not found" in response.json()["detail"]["error_message"]

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("amount", 0), ("amount", -1)])
    def test_create_transaction_deposit_invalid_value_amount_returns_400(
        self, api_client: APIClient, transaction_deposit_data: dict, field: str, value: int
    ) -> None:
        transaction_deposit_data[field] = value
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Amount must be positive" in response.json()["detail"]

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("account_id", 0), ("account_id", -1)])
    def test_create_transaction_deposit_invalid_value_account_id_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict, field: str, value: int
    ) -> None:
        transaction_deposit_data[field] = value
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert "Input should be greater than 0" in response.json()["detail"][0]["msg"]

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_invalid_type_account_id_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data["account_id"] = ""
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_invalid_type_amount_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data["amount"] = ""
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_invalid_type_transaction_type_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data["transaction_type"] = ""
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: unsupported transaction type")
    @pytest.mark.negative
    def test_create_transaction_deposit_invalid_value_transaction_type_returns_400(
        self, api_client: APIClient, user_account: dict
    ) -> None:
        response = api_client.post(
            Endpoints.TRANSACTIONS,
            json={
                "account_id": user_account["id"],
                "amount": 10,
                "transaction_type": "payment",
                "description": "",
            },
        )
        assert response.status_code == 400, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_missing_account_id_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data.pop("account_id")
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_missing_amount_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data.pop("amount")
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Deposit rejected: invalid input")
    @pytest.mark.negative
    def test_create_transaction_deposit_missing_transaction_type_returns_422(
        self, api_client: APIClient, transaction_deposit_data: dict
    ) -> None:
        transaction_deposit_data.pop("transaction_type")
        response = api_client.post(Endpoints.TRANSACTIONS, json=transaction_deposit_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Transaction History")
class TestGetTransactionsListByAccountId:
    @allure.story("Account transactions are listed and retrievable")
    @pytest.mark.smoke
    def test_get_transaction_list_by_account_id_response_200(
        self, api_client: APIClient, created_transaction_deposit: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction_by_account(created_transaction_deposit["account_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        transaction_list = response.json()
        assert isinstance(transaction_list, list)
        assert len(transaction_list) > 0
        transaction_new = next((t for t in transaction_list if t["id"] == created_transaction_deposit["id"]), None)
        assert transaction_new is not None
        assert transaction_new["id"] is not None
        assert transaction_new["amount"] is not None
        assert transaction_new["transaction_type"] is not None
        assert transaction_new["description"] is not None
        assert transaction_new["direction"] is not None
        assert transaction_new["created_at"] is not None

    @allure.story("Account transactions are listed and retrievable")
    def test_transaction_list_by_account_id_response_schema(
        self, api_client: APIClient, created_transaction_deposit: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction_by_account(created_transaction_deposit["account_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        transaction_schema = response.json()[0]
        assert isinstance(transaction_schema["id"], int)
        assert isinstance(transaction_schema["amount"], float)
        assert isinstance(transaction_schema["transaction_type"], str)
        assert isinstance(transaction_schema["description"], str)
        assert isinstance(transaction_schema["direction"], str)
        assert transaction_schema["created_at"] is not None

    @allure.story("Transaction lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_transaction_list_nonexistent_account_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.transaction_by_account(99999999))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Account not found" in response.json()["detail"]

    @allure.story("Transaction lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_transaction_list_invalid_type_account_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.transaction_by_account("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Transaction History")
class TestGetTransactionById:
    @allure.story("Account transactions are listed and retrievable")
    @pytest.mark.smoke
    def test_get_transaction_deposit_returns_200(
        self, api_client: APIClient, created_transaction_deposit: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction(created_transaction_deposit["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_order = response.json()
        assert new_order is not None
        assert new_order["id"] == created_transaction_deposit["id"]
        assert new_order["account_id"] == created_transaction_deposit["account_id"]
        assert new_order["amount"] == created_transaction_deposit["amount"]
        assert new_order["transaction_type"] == created_transaction_deposit["transaction_type"]
        assert new_order["description"] == created_transaction_deposit["description"]
        assert new_order["direction"] == created_transaction_deposit["direction"]
        assert new_order["created_at"] is not None

    @allure.story("Account transactions are listed and retrievable")
    def test_get_transaction_deposit_response_schema(
        self, api_client: APIClient, created_transaction_deposit: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction(created_transaction_deposit["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        order_schema = response.json()
        assert isinstance(order_schema["id"], int)
        assert isinstance(order_schema["account_id"], int)
        assert isinstance(order_schema["amount"], float)
        assert isinstance(order_schema["transaction_type"], str)
        assert isinstance(order_schema["description"], str)
        assert isinstance(order_schema["direction"], str)
        assert order_schema["created_at"] is not None

    @allure.story("Transaction lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_transaction_deposit_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.transaction(99999999))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Transaction not found" in response.json()["detail"]["error_message"]

    @allure.story("Transaction lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_transaction_deposit_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.transaction("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )
