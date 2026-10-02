"""API tests for /transfers: create transfer, read transfer transactions"""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints

pytestmark = [
    allure.epic("Transactions & Balance"),
    pytest.mark.api,
]


@allure.feature("Transfer")
class TestCreateTransfer:
    @allure.story("Transfer moves funds between accounts")
    @pytest.mark.smoke
    def test_create_transfer_returns_201(
        self,
        api_client: APIClient,
        user_account: dict,
        created_user: dict,
        created_recipient: dict,
        recipient_account: dict,
        transfer_data: dict,
        transaction_deposit_data: dict,
    ) -> None:
        with allure.step("Create transfer"):
            response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
            assert response.status_code == 201, f"Unexpected response: {response.text}"
            new_transfer = response.json()
        assert new_transfer is not None
        assert new_transfer["tx_out_id"] is not None
        assert new_transfer["tx_in_id"] is not None
        assert new_transfer["from_account_id"] == transfer_data["from_account_id"]
        assert new_transfer["to_account_id"] == transfer_data["to_account_id"]
        assert new_transfer["amount"] == transfer_data["amount"]
        assert new_transfer["description"] == transfer_data["description"]
        assert new_transfer["tx_out_created_at"] is not None
        assert new_transfer["tx_in_created_at"] is not None
        with allure.step("Check sender balance decreased"):
            response = api_client.get(Endpoints.accounts(created_user["id"]))
            assert response.status_code == 200, f"Unexpected response: {response.text}"
            account_list = response.json()
            assert isinstance(account_list, list)
            assert len(account_list) > 0
            account = next((a for a in account_list if a["id"] == user_account["id"]), None)
            assert account["balance"] == transaction_deposit_data["amount"] - transfer_data["amount"]
        with allure.step("Check recipient balance increased"):
            response = api_client.get(Endpoints.accounts(created_recipient["id"]))
            assert response.status_code == 200, f"Unexpected response: {response.text}"
            account_list = response.json()
            assert isinstance(account_list, list)
            assert len(account_list) > 0
            account = next((a for a in account_list if a["id"] == recipient_account["id"]), None)
            assert account["balance"] == transfer_data["amount"]

    @allure.story("Transfer moves funds between accounts")
    def test_transfer_data_response_schema(self, created_transfer: dict) -> None:
        assert isinstance(created_transfer["tx_out_id"], int)
        assert isinstance(created_transfer["tx_in_id"], int)
        assert isinstance(created_transfer["from_account_id"], int)
        assert isinstance(created_transfer["to_account_id"], int)
        assert isinstance(created_transfer["amount"], float)
        assert isinstance(created_transfer["description"], str)

    @allure.story("Transfer rejected: account not found")
    @pytest.mark.negative
    def test_create_transfer_nonexistent_from_account_id_returns_404(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data["from_account_id"] = 123123123
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Sender account not found" in response.json()["detail"]["error_message"]

    @allure.story("Transfer rejected: account not found")
    @pytest.mark.negative
    def test_create_transfer_nonexistent_to_account_id_returns_404(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data["to_account_id"] = 123123123
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Recipient account not found" in response.json()["detail"]["error_message"]

    @allure.story("Transfer rejected: insufficient funds")
    @pytest.mark.negative
    def test_create_transfer_insufficient_funds_returns_400(
        self, api_client: APIClient, transfer_data: dict, transaction_deposit_data: dict
    ) -> None:
        transfer_data["amount"] = transaction_deposit_data["amount"] + 1
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Insufficient funds" in response.json()["detail"]

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("amount", 0), ("amount", -1)])
    def test_create_transfer_invalid_value_amount_returns_400(
        self, api_client: APIClient, transfer_data: dict, field: str, value: int
    ) -> None:
        transfer_data[field] = value
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Amount must be positive" in response.json()["detail"]

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("from_account_id", 0), ("from_account_id", -1)])
    def test_create_transfer_invalid_value_from_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict, field: str, value: int
    ) -> None:
        transfer_data[field] = value
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert "Input should be greater than 0" in response.json()["detail"][0]["msg"]

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("to_account_id", 0), ("to_account_id", -1)])
    def test_create_transfer_invalid_value_to_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict, field: str, value: int
    ) -> None:
        transfer_data[field] = value
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert "Input should be greater than 0" in response.json()["detail"][0]["msg"]

    @allure.story("Transfer rejected: same account")
    @pytest.mark.negative
    def test_create_transfer_same_account_id_returns_400(self, api_client: APIClient, transfer_data: dict) -> None:
        transfer_data["from_account_id"] = transfer_data["to_account_id"]
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Cannot transfer to the same account" in response.json()["detail"]

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_invalid_type_from_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data["from_account_id"] = ""
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_invalid_type_to_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data["to_account_id"] = ""
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_invalid_type_amount_returns_422(self, api_client: APIClient, transfer_data: dict) -> None:
        transfer_data["amount"] = ""
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_missing_from_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data.pop("from_account_id")
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_missing_to_account_id_returns_422(
        self, api_client: APIClient, transfer_data: dict
    ) -> None:
        transfer_data.pop("to_account_id")
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Transfer rejected: invalid input")
    @pytest.mark.negative
    def test_create_transfer_missing_amount_returns_422(self, api_client: APIClient, transfer_data: dict) -> None:
        transfer_data.pop("amount")
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Transaction History")
class TestGetTransfersListByAccountId:
    @allure.story("Account transactions are listed and retrievable")
    def test_get_transfer_list_by_from_account_id_response_200(
        self, api_client: APIClient, created_transfer: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction_by_account(created_transfer["from_account_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        transfers_list = response.json()
        assert isinstance(transfers_list, list)
        assert len(transfers_list) > 0
        transfer_out = next((t for t in transfers_list if t["id"] == created_transfer["tx_out_id"]), None)
        assert transfer_out is not None
        assert transfer_out["amount"] is not None
        assert transfer_out["transaction_type"] == "transfer"
        assert transfer_out["description"] is not None
        assert transfer_out["direction"] == "out"
        assert transfer_out["created_at"] is not None

    @allure.story("Account transactions are listed and retrievable")
    def test_get_transfer_list_by_to_account_id_response_200(
        self, api_client: APIClient, created_transfer: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction_by_account(created_transfer["to_account_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        transfers_list = response.json()
        assert isinstance(transfers_list, list)
        assert len(transfers_list) > 0
        transfer_in = next((t for t in transfers_list if t["id"] == created_transfer["tx_in_id"]), None)
        assert transfer_in is not None
        assert transfer_in["amount"] is not None
        assert transfer_in["transaction_type"] == "transfer"
        assert transfer_in["description"] is not None
        assert transfer_in["direction"] == "in"
        assert transfer_in["created_at"] is not None


@allure.feature("Transaction History")
class TestGetTransfersById:
    @allure.story("Account transactions are listed and retrievable")
    def test_get_transfer_tx_out_id_returns_200(self, api_client: APIClient, created_transfer: dict) -> None:
        response = api_client.get(Endpoints.transaction(created_transfer["tx_out_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_transfer_out = response.json()
        assert new_transfer_out is not None
        assert new_transfer_out["id"] == created_transfer["tx_out_id"]
        assert new_transfer_out["account_id"] == created_transfer["from_account_id"]
        assert new_transfer_out["amount"] == created_transfer["amount"]
        assert new_transfer_out["description"] == created_transfer["description"]
        assert new_transfer_out["direction"] == "out"
        assert new_transfer_out["created_at"] is not None

    @allure.story("Account transactions are listed and retrievable")
    def test_get_transfer_tx_in_id_returns_200(self, api_client: APIClient, created_transfer: dict) -> None:
        response = api_client.get(Endpoints.transaction(created_transfer["tx_in_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_transfer_in = response.json()
        assert new_transfer_in is not None
        assert new_transfer_in["id"] == created_transfer["tx_in_id"]
        assert new_transfer_in["account_id"] == created_transfer["to_account_id"]
        assert new_transfer_in["amount"] == created_transfer["amount"]
        assert new_transfer_in["description"] == created_transfer["description"]
        assert new_transfer_in["direction"] == "in"
        assert new_transfer_in["created_at"] is not None
