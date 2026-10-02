"""DB checks for deposits: transaction record, account balance and transaction history."""

import allure
import pytest

from database.db_manager import DBManager

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.db]


@allure.feature("Deposit")
class TestCreateTransactionDepositDB:
    @allure.story("Deposit increases account balance")
    def test_created_transaction_deposit_saved_in_db(self, created_transaction_deposit: dict, db: DBManager) -> None:
        deposit_in_db = db.get_transaction_by_id(created_transaction_deposit["id"])
        assert deposit_in_db is not None
        assert deposit_in_db["id"] == created_transaction_deposit["id"]
        assert deposit_in_db["account_id"] == created_transaction_deposit["account_id"]
        assert deposit_in_db["amount"] == created_transaction_deposit["amount"]
        assert deposit_in_db["transaction_type"] == "deposit"
        assert deposit_in_db["direction"] == "in"
        assert deposit_in_db["description"] == created_transaction_deposit["description"]
        assert deposit_in_db["created_at"] is not None

    @allure.story("Deposit increases account balance")
    def test_created_transaction_deposit_schema(self, created_transaction_deposit: dict, db: DBManager) -> None:
        transaction_schema = db.get_transaction_by_id(created_transaction_deposit["id"])
        assert isinstance(transaction_schema["id"], int)
        assert isinstance(transaction_schema["account_id"], int)
        assert isinstance(transaction_schema["amount"], float)
        assert isinstance(transaction_schema["transaction_type"], str)
        assert isinstance(transaction_schema["direction"], str)
        assert isinstance(transaction_schema["description"], str)

    @allure.story("Deposit increases account balance")
    def test_created_transaction_deposit_increases_account_balance_in_db(
        self, created_transaction_deposit: dict, db: DBManager
    ) -> None:
        deposit_in_db = db.get_transaction_by_id(created_transaction_deposit["id"])
        account_in_db = db.get_account_balance(created_transaction_deposit["account_id"])
        assert account_in_db == deposit_in_db["amount"]


@allure.feature("Transaction History")
class TestCountTransactionsForAccountDB:
    @allure.story("Account transactions are listed and retrievable")
    def test_count_transactions_for_account_saved_in_db(self, created_transaction_deposit: dict, db: DBManager) -> None:
        count = db.count_transactions_for_account(created_transaction_deposit["account_id"])
        assert count == 1


@allure.feature("Transaction History")
class TestGetTransactionsByAccountDB:
    @allure.story("Account transactions are listed and retrievable")
    def test_latest_transaction_matches_created_deposit(self, created_transaction_deposit: dict, db: DBManager) -> None:
        transactions = db.get_transactions_by_account(created_transaction_deposit["account_id"])
        latest = transactions[0]
        assert latest["id"] == created_transaction_deposit["id"]
