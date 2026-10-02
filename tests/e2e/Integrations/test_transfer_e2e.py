"""E2E integration (API + DB): a transfer moves funds between accounts and saves both transactions in the DB."""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints
from database.db_manager import DBManager

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.integration]


@allure.feature("Transfer")
class TestE2ETransfer:
    @allure.story("Transfer moves funds between accounts")
    @allure.title("Transfer via API moves funds between accounts and saves both transactions in DB")
    def test_e2e_transfer(
        self,
        api_client: APIClient,
        created_transaction_deposit: dict,
        created_user: dict,
        created_recipient: dict,
        transfer_data: dict,
        db: DBManager,
    ) -> None:
        with allure.step("Get recipient balance before transfer"):
            response_before_recipient = api_client.get(
                Endpoints.accounts_by_account_number(created_recipient["account_number"])
            )
            assert response_before_recipient.status_code == 200, f"Unexpected response: {response_before_recipient.text}"
            balance_recipient_before = response_before_recipient.json()["balance"]

        with allure.step("Transfer funds via API"):
            transfer_response = api_client.post(Endpoints.TRANSFERS, json=transfer_data)
            assert transfer_response.status_code == 201, f"Unexpected response: {transfer_response.text}"
            created_transfer = transfer_response.json()

        with allure.step("Balances of sender and recipient are updated"):
            response1 = api_client.get(Endpoints.accounts_by_account_number(created_user["account_number"]))
            assert response1.status_code == 200, f"Unexpected response: {response1.text}"
            account_created_user = response1.json()

            response2 = api_client.get(Endpoints.accounts_by_account_number(created_recipient["account_number"]))
            assert response2.status_code == 200, f"Unexpected response: {response2.text}"
            account_created_recipient = response2.json()

            assert account_created_user["balance"] == created_transaction_deposit["amount"] - transfer_data["amount"]
            assert account_created_recipient["balance"] == balance_recipient_before + transfer_data["amount"]

        with allure.step("Outgoing and incoming transactions are saved in DB"):
            transfer_in_db1 = db.get_transaction_by_id(created_transfer["tx_out_id"])
            assert transfer_in_db1 is not None
            assert transfer_in_db1["amount"] == transfer_data["amount"]
            assert transfer_in_db1["transaction_type"] == "transfer"

            transfer_in_db2 = db.get_transaction_by_id(created_transfer["tx_in_id"])
            assert transfer_in_db2 is not None
            assert transfer_in_db2["amount"] == transfer_data["amount"]
            assert transfer_in_db2["transaction_type"] == "transfer"
