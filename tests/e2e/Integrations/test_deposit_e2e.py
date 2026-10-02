"""E2E integration (API + DB): a deposit updates the account balance and is saved in the DB."""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints
from database.db_manager import DBManager

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.integration]


@allure.feature("Deposit")
class TestE2EBankDeposit:
    @allure.story("Deposit increases account balance")
    @allure.title("Deposit via API updates account balance and is saved in DB")
    def test_e2e_deposit(
        self, api_client: APIClient, created_transaction_deposit: dict, created_user: dict, db: DBManager
    ) -> None:
        with allure.step("Account balance equals the deposit"):
            response = api_client.get(Endpoints.accounts_by_account_number(created_user["account_number"]))
            assert response.status_code == 200, f"Unexpected response: {response.text}"
            account = response.json()
            assert account["balance"] == created_transaction_deposit["amount"]

        with allure.step("Deposit is saved in DB"):
            deposit_in_db = db.get_transaction_by_id(created_transaction_deposit["id"])
            assert deposit_in_db is not None
            assert deposit_in_db["amount"] == created_transaction_deposit["amount"]
            assert deposit_in_db["transaction_type"] == "deposit"
