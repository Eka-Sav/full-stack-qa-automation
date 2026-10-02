"""DB checks for transfers: outgoing and incoming records and balances of both accounts."""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints
from database.db_manager import DBManager

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.db]


@allure.feature("Transfer")
class TestCreateTransactionTransferDB:
    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_out_saved_in_db(self, created_transfer: dict, db: DBManager) -> None:
        transfer_out_in_db = db.get_transaction_by_id(created_transfer["tx_out_id"])
        assert transfer_out_in_db is not None
        assert transfer_out_in_db["id"] == created_transfer["tx_out_id"]
        assert transfer_out_in_db["account_id"] == created_transfer["from_account_id"]
        assert transfer_out_in_db["amount"] == created_transfer["amount"]
        assert transfer_out_in_db["transaction_type"] == "transfer"
        assert transfer_out_in_db["direction"] == "out"
        assert transfer_out_in_db["description"] is not None
        assert transfer_out_in_db["created_at"] is not None

    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_in_saved_in_db(self, created_transfer: dict, db: DBManager) -> None:
        transfer_in_in_db = db.get_transaction_by_id(created_transfer["tx_in_id"])
        assert transfer_in_in_db is not None
        assert transfer_in_in_db["id"] == created_transfer["tx_in_id"]
        assert transfer_in_in_db["account_id"] == created_transfer["to_account_id"]
        assert transfer_in_in_db["amount"] == created_transfer["amount"]
        assert transfer_in_in_db["transaction_type"] == "transfer"
        assert transfer_in_in_db["direction"] == "in"
        assert transfer_in_in_db["description"] is not None
        assert transfer_in_in_db["created_at"] is not None

    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_out_schema(self, created_transfer: dict, db: DBManager) -> None:
        transaction_schema = db.get_transaction_by_id(created_transfer["tx_out_id"])
        assert isinstance(transaction_schema["id"], int)
        assert isinstance(transaction_schema["account_id"], int)
        assert isinstance(transaction_schema["amount"], float)
        assert isinstance(transaction_schema["transaction_type"], str)
        assert isinstance(transaction_schema["direction"], str)
        assert isinstance(transaction_schema["description"], str)

    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_in_schema(self, created_transfer: dict, db: DBManager) -> None:
        transaction_schema = db.get_transaction_by_id(created_transfer["tx_in_id"])
        assert isinstance(transaction_schema["id"], int)
        assert isinstance(transaction_schema["account_id"], int)
        assert isinstance(transaction_schema["amount"], float)
        assert isinstance(transaction_schema["transaction_type"], str)
        assert isinstance(transaction_schema["direction"], str)
        assert isinstance(transaction_schema["description"], str)

    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_sender_balance_decreases_in_db(
        self,
        api_client: APIClient,
        created_transaction_deposit: dict,
        user_account: dict,
        transfer_data: dict,
        db: DBManager,
    ) -> None:
        balance_before = db.get_account_balance(user_account["id"])
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        transfer_out = response.json()
        balance_after = db.get_account_balance(user_account["id"])
        assert balance_after == balance_before - transfer_out["amount"]

    @allure.story("Transfer moves funds between accounts")
    def test_created_transaction_transfer_recipient_balance_increases_in_db(
        self,
        api_client: APIClient,
        created_transaction_deposit: dict,
        recipient_account: dict,
        transfer_data: dict,
        db: DBManager,
    ) -> None:
        balance_before = db.get_account_balance(recipient_account["id"])
        response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        transfer_in = response.json()
        balance_after = db.get_account_balance(recipient_account["id"])
        assert balance_after == balance_before + transfer_in["amount"]
