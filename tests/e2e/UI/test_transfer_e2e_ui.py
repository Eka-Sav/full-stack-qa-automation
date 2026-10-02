"""E2E: a transfer made via UI updates balances and stats of both users in the UI and in the DB."""

import allure
import pytest
from playwright.sync_api import Page, expect

from config.config import config
from database.db_manager import DBManager
from pages.dashboard_page import DashboardPage
from pages.transactions_page import TransactionsPage

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.e2e]


@allure.feature("Transfer")
class TestE2ETransferUI:
    @allure.story("Transfer moves funds between accounts")
    @allure.title("Transfer via UI updates balances and stats of sender and recipient in UI and DB")
    def test_e2e_transfer(
        self,
        created_transaction_deposit: dict,
        user_account: dict,
        recipient_account: dict,
        logged_in_page_recipient: Page,
        transactions_page: TransactionsPage,
        transactions_page_recipient: TransactionsPage,
        dashboard_page_sender: DashboardPage,
        dashboard_page_recipient: DashboardPage,
        db: DBManager,
    ) -> None:
        transfer_amount = 50.0

        with allure.step("Before transfer: sender Transactions page balance matches DB"):
            expect(transactions_page.balance_amount).to_have_text(f"${created_transaction_deposit['amount']:.2f}")
            sender_tx_balance_before = transactions_page.get_balance()
            sender_tx_balance_before_db = db.get_account_balance(user_account["id"])
            assert sender_tx_balance_before == sender_tx_balance_before_db

        with allure.step("Before transfer: sender Dashboard stats match DB"):
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${created_transaction_deposit['amount']:.2f}")
            sender_dash_balance_before = dashboard_page_sender.get_balance()
            sender_dash_received_before = dashboard_page_sender.get_total_received()
            sender_dash_spent_before = dashboard_page_sender.get_total_spent()
            sender_dash_count_before = dashboard_page_sender.get_transactions_count()

            sender_dash_balance_before_db = db.get_account_balance(user_account["id"])
            sender_dash_received_before_db = db.get_total_received(user_account["id"])
            sender_dash_spent_before_db = db.get_total_spent(user_account["id"])

            assert sender_dash_balance_before == sender_dash_balance_before_db
            assert sender_dash_received_before == sender_dash_received_before_db
            assert sender_dash_spent_before == sender_dash_spent_before_db
            assert sender_dash_count_before == 1

        with allure.step("Before transfer: recipient Transactions page balance matches DB"):
            recipient_tx_balance_before = transactions_page_recipient.get_balance()
            recipient_tx_balance_before_db = db.get_account_balance(recipient_account["id"])
            assert recipient_tx_balance_before == recipient_tx_balance_before_db

        with allure.step("Before transfer: recipient Dashboard stats match DB"):
            dashboard_page_recipient.page.goto(f"{config.FRONTEND_URL}/dashboard")

            recipient_dash_balance_before = dashboard_page_recipient.get_balance()
            recipient_dash_received_before = dashboard_page_recipient.get_total_received()
            recipient_dash_spent_before = dashboard_page_recipient.get_total_spent()
            recipient_dash_count_before = dashboard_page_recipient.get_transactions_count()

            recipient_dash_balance_before_db = db.get_account_balance(recipient_account["id"])
            recipient_dash_received_before_db = db.get_total_received(recipient_account["id"])
            recipient_dash_spent_before_db = db.get_total_spent(recipient_account["id"])

            assert recipient_dash_balance_before == recipient_dash_balance_before_db
            assert recipient_dash_received_before == recipient_dash_received_before_db
            assert recipient_dash_spent_before == recipient_dash_spent_before_db
            assert recipient_dash_count_before == 0

        with allure.step(f"Transfer {transfer_amount} to the recipient via UI"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            number_recipient_account = recipient_account["account_number"]
            transactions_page.confirm_send_transfer(str(transfer_amount), "test transfer", number_recipient_account)
            expect(transactions_page.transaction_success).to_be_visible()

        with allure.step("After transfer: sender Transactions page balance matches DB"):
            expected_balance = sender_tx_balance_before - transfer_amount
            expect(transactions_page.balance_amount).to_have_text(f"${expected_balance:.2f}")
            sender_tx_balance_after = transactions_page.get_balance()
            sender_tx_balance_after_db = db.get_account_balance(user_account["id"])
            assert sender_tx_balance_after == sender_tx_balance_after_db

        with allure.step("After transfer: sender Dashboard stats match DB"):
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${expected_balance:.2f}")

            sender_dash_balance_after = dashboard_page_sender.get_balance()
            sender_dash_received_after = dashboard_page_sender.get_total_received()
            sender_dash_spent_after = dashboard_page_sender.get_total_spent()
            sender_dash_count_after = dashboard_page_sender.get_transactions_count()

            sender_dash_balance_after_db = db.get_account_balance(user_account["id"])
            sender_dash_received_after_db = db.get_total_received(user_account["id"])
            sender_dash_spent_after_db = db.get_total_spent(user_account["id"])

            assert sender_tx_balance_after == sender_dash_balance_after_db
            assert sender_dash_balance_after == sender_dash_balance_after_db
            assert sender_dash_balance_after_db == sender_dash_balance_before - transfer_amount

            assert sender_dash_received_after == sender_dash_received_after_db
            assert sender_dash_received_after_db == sender_dash_received_before

            assert sender_dash_spent_after == sender_dash_spent_after_db
            assert sender_dash_spent_after_db == sender_dash_spent_before + transfer_amount
            assert sender_dash_count_after == 2

        with allure.step("After transfer: sender Dashboard transfer appears in history"):
            last_transaction = dashboard_page_sender.get_latest_transaction_amount()
            assert last_transaction == transfer_amount

        with allure.step("After transfer: recipient Transactions page balance matches DB"):
            expected_balance = recipient_tx_balance_before + transfer_amount
            transactions_page_recipient.page.reload()
            expect(transactions_page_recipient.balance_amount).to_have_text(f"${expected_balance:.2f}")
            recipient_tx_balance_after = transactions_page_recipient.get_balance()
            recipient_tx_balance_after_db = db.get_account_balance(recipient_account["id"])
            assert recipient_tx_balance_after == recipient_tx_balance_after_db

        with allure.step("After transfer: recipient Dashboard stats match DB"):
            dashboard_page_recipient.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_recipient.balance_amount).to_have_text(f"${expected_balance:.2f}")

            recipient_dash_balance_after = dashboard_page_recipient.get_balance()
            recipient_dash_received_after = dashboard_page_recipient.get_total_received()
            recipient_dash_spent_after = dashboard_page_recipient.get_total_spent()
            recipient_dash_count_after = dashboard_page_recipient.get_transactions_count()

            recipient_dash_balance_after_db = db.get_account_balance(recipient_account["id"])
            recipient_dash_received_after_db = db.get_total_received(recipient_account["id"])
            recipient_dash_spent_after_db = db.get_total_spent(recipient_account["id"])

            assert recipient_dash_balance_after == recipient_dash_balance_after_db
            assert recipient_dash_balance_after == recipient_dash_balance_before + transfer_amount

            assert recipient_dash_received_after == recipient_dash_received_after_db
            assert recipient_dash_received_after == recipient_dash_received_before + transfer_amount

            assert recipient_dash_spent_after == recipient_dash_spent_after_db
            assert recipient_dash_spent_after == recipient_dash_spent_before

            assert recipient_dash_count_after == 1

        with allure.step("After transfer: recipient Dashboard transfer appears in history"):
            last_transaction = dashboard_page_recipient.get_latest_transaction_amount()
            assert last_transaction == transfer_amount

    @pytest.mark.negative
    @allure.story("Transfer rejected: insufficient funds")
    @allure.title("Transfer exceeding the balance via UI is rejected and sender stats stay unchanged")
    def test_e2e_transfer_negative(
        self,
        created_transaction_deposit: dict,
        user_account: dict,
        recipient_account: dict,
        transactions_page: TransactionsPage,
        dashboard_page_sender: DashboardPage,
        db: DBManager,
    ) -> None:
        transfer_amount = 20000.0

        with allure.step("Before transfer: sender Transactions page balance matches DB"):
            expect(transactions_page.balance_amount).to_have_text(f"${created_transaction_deposit['amount']:.2f}")
            sender_tx_balance_before = transactions_page.get_balance()
            sender_tx_balance_before_db = db.get_account_balance(user_account["id"])
            assert sender_tx_balance_before == sender_tx_balance_before_db

        with allure.step("Before transfer: sender Dashboard stats match DB"):
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${created_transaction_deposit['amount']:.2f}")
            sender_dash_balance_before = dashboard_page_sender.get_balance()
            sender_dash_received_before = dashboard_page_sender.get_total_received()
            sender_dash_spent_before = dashboard_page_sender.get_total_spent()
            sender_dash_count_before = dashboard_page_sender.get_transactions_count()

            sender_dash_balance_before_db = db.get_account_balance(user_account["id"])
            sender_dash_received_before_db = db.get_total_received(user_account["id"])
            sender_dash_spent_before_db = db.get_total_spent(user_account["id"])

            assert sender_dash_balance_before == sender_dash_balance_before_db
            assert sender_dash_received_before == sender_dash_received_before_db
            assert sender_dash_spent_before == sender_dash_spent_before_db
            assert sender_dash_count_before == 1

        with allure.step(f"Try to transfer {transfer_amount} via UI and get an error"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            number_recipient_account = recipient_account["account_number"]
            transactions_page.confirm_send_transfer(str(transfer_amount), "test transfer", number_recipient_account)
            expect(transactions_page.transaction_error).to_be_visible()

        with allure.step("After rejected transfer: sender balance and stats are unchanged"):
            expect(transactions_page.balance_amount).to_have_text(f"${sender_tx_balance_before:.2f}")
            sender_tx_balance_after = transactions_page.get_balance()
            assert sender_tx_balance_after == sender_tx_balance_before
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${sender_tx_balance_before:.2f}")
            sender_dash_balance_after = dashboard_page_sender.get_balance()
            sender_dash_received_after = dashboard_page_sender.get_total_received()
            sender_dash_spent_after = dashboard_page_sender.get_total_spent()
            sender_dash_count_after = dashboard_page_sender.get_transactions_count()

            sender_dash_balance_after_db = db.get_account_balance(user_account["id"])
            sender_dash_received_after_db = db.get_total_received(user_account["id"])
            sender_dash_spent_after_db = db.get_total_spent(user_account["id"])

            assert sender_tx_balance_after == sender_dash_balance_after_db
            assert sender_dash_balance_after == sender_dash_balance_after_db
            assert sender_dash_balance_after_db == sender_dash_balance_before

            assert sender_dash_received_after == sender_dash_received_after_db
            assert sender_dash_received_after_db == sender_dash_received_before

            assert sender_dash_spent_after == sender_dash_spent_after_db
            assert sender_dash_spent_after_db == sender_dash_spent_before
            assert sender_dash_count_after == sender_dash_count_before

        with allure.step("After rejected transfer: sender Dashboard history is unchanged"):
            last_transaction = dashboard_page_sender.get_latest_transaction_amount()
            assert last_transaction == created_transaction_deposit["amount"]
