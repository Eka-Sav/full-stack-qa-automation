"""E2E: a deposit made via UI is reflected on the transactions page, the dashboard and in the DB."""

import allure
import pytest
from playwright.sync_api import expect

from config.config import config
from database.db_manager import DBManager
from pages.dashboard_page import DashboardPage
from pages.transactions_page import TransactionsPage

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.e2e, pytest.mark.ai_generated]


@allure.feature("Deposit")
class TestE2EDepositUI:
    @allure.story("Deposit increases account balance")
    @allure.title("Deposit via UI is reflected on transactions page, dashboard and in DB")
    def test_e2e_deposit(
        self,
        user_account: dict,
        transactions_page: TransactionsPage,
        dashboard_page_sender: DashboardPage,
        db: DBManager,
    ) -> None:
        DEPOSIT_AMOUNT = 100.0
        account_id = user_account["id"]

        with allure.step("Before deposit: Transactions page balance matches DB"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            tx_balance_before = transactions_page.get_balance()
            tx_balance_before_db = db.get_account_balance(account_id)

            assert tx_balance_before == 0.0, f"Expected zero balance on Transactions page, got {tx_balance_before}"
            assert tx_balance_before_db == 0.0, f"Expected zero balance in DB, got {tx_balance_before_db}"
            assert tx_balance_before == tx_balance_before_db, (
                f"UI balance {tx_balance_before} != DB balance {tx_balance_before_db}"
            )

        with allure.step("Before deposit: Dashboard stats are zero and match DB"):
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")
            dash_balance_before = dashboard_page_sender.get_balance()
            dash_received_before = dashboard_page_sender.get_total_received()
            dash_spent_before = dashboard_page_sender.get_total_spent()
            dash_count_before = dashboard_page_sender.get_transactions_count()

            dash_balance_before_db = db.get_account_balance(account_id)
            dash_received_before_db = db.get_total_received(account_id)
            dash_spent_before_db = db.get_total_spent(account_id)

            assert dash_balance_before == 0.0, f"Expected zero balance on Dashboard, got {dash_balance_before}"
            assert dash_balance_before == dash_balance_before_db, (
                f"Dashboard balance {dash_balance_before} != DB balance {dash_balance_before_db}"
            )
            assert dash_received_before == 0.0, f"Expected zero Total Received, got {dash_received_before}"
            assert dash_received_before == dash_received_before_db, (
                f"Dashboard Total Received {dash_received_before} != DB {dash_received_before_db}"
            )
            assert dash_spent_before == 0.0, f"Expected zero Total Spent, got {dash_spent_before}"
            assert dash_spent_before == dash_spent_before_db, (
                f"Dashboard Total Spent {dash_spent_before} != DB {dash_spent_before_db}"
            )
            assert dash_count_before == 0, f"Expected no transactions, got {dash_count_before}"

        with allure.step(f"Make a deposit of {DEPOSIT_AMOUNT} via UI"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            transactions_page.confirm_send_deposit(str(DEPOSIT_AMOUNT), "test deposit")
            expect(transactions_page.transaction_success).to_be_visible()

        with allure.step("After deposit: Transactions page balance matches DB"):
            expected_balance = tx_balance_before_db + DEPOSIT_AMOUNT
            expect(transactions_page.balance_amount).to_have_text(f"${expected_balance:.2f}")
            tx_balance_after = transactions_page.get_balance()
            tx_balance_after_db = db.get_account_balance(account_id)

            assert tx_balance_after == tx_balance_after_db, (
                f"UI balance {tx_balance_after} != DB balance {tx_balance_after_db}"
            )
            assert tx_balance_after_db == tx_balance_before_db + DEPOSIT_AMOUNT, (
                f"DB balance {tx_balance_after_db} != {tx_balance_before_db} + {DEPOSIT_AMOUNT}"
            )

        with allure.step("After deposit: Dashboard stats match DB"):
            # open the dashboard again, otherwise it may still show stats from before the deposit
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${expected_balance:.2f}")
            dash_balance_after = dashboard_page_sender.get_balance()
            dash_received_after = dashboard_page_sender.get_total_received()
            dash_spent_after = dashboard_page_sender.get_total_spent()
            dash_count_after = dashboard_page_sender.get_transactions_count()

            dash_balance_after_db = db.get_account_balance(account_id)
            dash_received_after_db = db.get_total_received(account_id)
            dash_spent_after_db = db.get_total_spent(account_id)

            assert dash_balance_after == dash_balance_after_db, (
                f"Dashboard balance {dash_balance_after} != DB balance {dash_balance_after_db}"
            )
            assert dash_balance_after_db == dash_balance_before + DEPOSIT_AMOUNT, (
                f"DB balance {dash_balance_after_db} != expected {dash_balance_before + DEPOSIT_AMOUNT}"
            )

            assert dash_received_after == dash_received_after_db, (
                f"Dashboard Total Received {dash_received_after} != DB {dash_received_after_db}"
            )
            assert dash_received_after_db == dash_received_before + DEPOSIT_AMOUNT, (
                f"DB Total Received {dash_received_after_db} != expected {dash_received_before + DEPOSIT_AMOUNT}"
            )

            # a deposit must not affect outgoing totals
            assert dash_spent_after == dash_spent_after_db, (
                f"Dashboard Total Spent {dash_spent_after} != DB {dash_spent_after_db}"
            )
            assert dash_spent_after_db == dash_spent_before, (
                f"Total Spent changed after deposit: {dash_spent_before} -> {dash_spent_after_db}"
            )

            assert dash_count_after == dash_count_before + 1, (
                f"Expected {dash_count_before + 1} transactions, got {dash_count_after}"
            )

        with allure.step("Deposit appears in Dashboard transaction history"):
            last_transaction = dashboard_page_sender.get_latest_transaction_amount()
            assert last_transaction == DEPOSIT_AMOUNT, (
                f"Last transaction amount {last_transaction} != deposit {DEPOSIT_AMOUNT}"
            )
