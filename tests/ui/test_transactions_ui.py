"""UI tests for the transactions page: deposit and transfer forms."""

import allure
import pytest
from playwright.sync_api import Page, expect

from config.config import config
from pages.dashboard_page import DashboardPage
from pages.transactions_page import TransactionsPage

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.ui]


@allure.feature("Deposit")
class TestTransactionsDepositPage:
    @allure.story("Deposit increases account balance")
    @allure.title("Deposit updates balance and dashboard stats")
    def test_deposit_success(self, transactions_page: TransactionsPage, dashboard_page_sender: DashboardPage) -> None:
        DEPOSIT_AMOUNT = 101.0

        with allure.step("Before deposit: read balance on the transactions page"):
            amount_before = transactions_page.get_balance()
        with allure.step("Before deposit: dashboard stats are zero and match the balance"):
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")

            dashboard_balance_before = dashboard_page_sender.get_balance()
            dashboard_received_before = dashboard_page_sender.get_total_received()
            dashboard_spent_before = dashboard_page_sender.get_total_spent()
            dashboard_count_before = dashboard_page_sender.get_transactions_count()

            assert dashboard_balance_before == amount_before
            assert dashboard_received_before == amount_before
            assert dashboard_spent_before == 0.0
            assert dashboard_count_before == 0

        with allure.step("Make a deposit"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            transactions_page.confirm_send_deposit(str(DEPOSIT_AMOUNT), "deposit 1")
            expect(transactions_page.transaction_success).to_be_visible()

        with allure.step("After deposit: balance on the transactions page increased"):
            expect(transactions_page.balance_amount).to_have_text(f"${amount_before + DEPOSIT_AMOUNT:.2f}")
            amount_after = transactions_page.get_balance()
            assert amount_after == amount_before + DEPOSIT_AMOUNT

        with allure.step("After deposit: dashboard stats are updated"):
            dashboard_page_sender.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${amount_after:.2f}")

            dashboard_balance_after = dashboard_page_sender.get_balance()
            dashboard_received_after = dashboard_page_sender.get_total_received()
            dashboard_spent_after = dashboard_page_sender.get_total_spent()
            dashboard_count_after = dashboard_page_sender.get_transactions_count()

            assert dashboard_balance_after == amount_after
            assert dashboard_received_after == dashboard_received_before + DEPOSIT_AMOUNT
            assert dashboard_spent_after == dashboard_spent_before
            assert dashboard_count_after == dashboard_count_before + 1

        with allure.step("After deposit: new transaction is shown in the dashboard history"):
            latest_amount = dashboard_page_sender.get_latest_transaction_amount()
            assert latest_amount == DEPOSIT_AMOUNT

    @pytest.mark.negative
    @allure.story("Deposit rejected: invalid input")
    @allure.title("Deposit with invalid amount: '{value}'")
    @pytest.mark.parametrize("value", ["0", "-100", "", " "])
    def test_deposit_invalid_amount(self, transactions_page: TransactionsPage, value: str) -> None:
        transactions_page.confirm_send_deposit(value, "deposit 1")
        expect(transactions_page.transaction_error).to_be_visible()


@allure.feature("Transfer")
class TestTransactionsTransferPage:
    @allure.story("Transfer moves funds between accounts")
    @allure.title("Transfer updates balances and dashboard stats of both users")
    def test_transfer_success(
        self,
        transactions_page_with_deposit: TransactionsPage,
        recipient_account: dict,
        logged_in_page_recipient: Page,
        transactions_page_recipient: TransactionsPage,
        dashboard_page_sender: DashboardPage,
        dashboard_page_recipient: DashboardPage,
    ) -> None:
        TRANSFER_AMOUNT = 50.0

        with allure.step("Before transfer: sender balance on the transactions page"):
            expect(transactions_page_with_deposit.balance_amount).not_to_have_text("$0.00")
            sender_tx_balance_before = transactions_page_with_deposit.get_balance()

        with allure.step("Before transfer: sender dashboard stats match the deposit"):
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${sender_tx_balance_before:.2f}")
            sender_dash_balance_before = dashboard_page_sender.get_balance()
            sender_dash_received_before = dashboard_page_sender.get_total_received()
            sender_dash_spent_before = dashboard_page_sender.get_total_spent()
            sender_dash_count_before = dashboard_page_sender.get_transactions_count()

            assert sender_dash_balance_before == sender_tx_balance_before
            assert sender_dash_received_before == sender_tx_balance_before
            assert sender_dash_spent_before == 0.0
            assert sender_dash_count_before == 1

        with allure.step("Before transfer: recipient balance on the transactions page"):
            recipient_tx_balance_before = transactions_page_recipient.get_balance()

        with allure.step("Before transfer: recipient dashboard stats are zero"):
            dashboard_page_recipient.page.goto(f"{config.FRONTEND_URL}/dashboard")
            recipient_dash_balance_before = dashboard_page_recipient.get_balance()
            recipient_dash_received_before = dashboard_page_recipient.get_total_received()
            recipient_dash_spent_before = dashboard_page_recipient.get_total_spent()
            recipient_dash_count_before = dashboard_page_recipient.get_transactions_count()

            assert recipient_dash_balance_before == recipient_tx_balance_before
            assert recipient_dash_received_before == recipient_tx_balance_before
            assert recipient_dash_spent_before == 0.0
            assert recipient_dash_count_before == 0

        with allure.step("Send a transfer to the recipient"):
            transactions_page_with_deposit.page.goto(f"{config.FRONTEND_URL}/transactions")
            number_recipient_account = recipient_account["account_number"]
            transactions_page_with_deposit.confirm_send_transfer(
                str(TRANSFER_AMOUNT), "transfer", number_recipient_account
            )
            expect(transactions_page_with_deposit.transaction_success).to_be_visible()

        with allure.step("After transfer: sender balance on the transactions page"):
            expect(transactions_page_with_deposit.balance_amount).to_have_text(
                f"${sender_tx_balance_before - TRANSFER_AMOUNT:.2f}"
            )
            sender_tx_balance_after = transactions_page_with_deposit.get_balance()

        with allure.step("After transfer: sender dashboard stats are updated"):
            transactions_page_with_deposit.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_sender.balance_amount).to_have_text(f"${sender_tx_balance_after:.2f}")
            sender_dash_balance_after = dashboard_page_sender.get_balance()
            sender_dash_received_after = dashboard_page_sender.get_total_received()
            sender_dash_spent_after = dashboard_page_sender.get_total_spent()
            sender_dash_count_after = dashboard_page_sender.get_transactions_count()

            assert sender_tx_balance_after == sender_dash_balance_after
            assert sender_dash_balance_after == sender_dash_balance_before - TRANSFER_AMOUNT
            assert sender_dash_received_after == sender_dash_received_before
            assert sender_dash_spent_after == sender_dash_spent_before + TRANSFER_AMOUNT
            assert sender_dash_count_after == 2

        with allure.step("After transfer: transfer is shown in the sender dashboard history"):
            latest_amount = dashboard_page_sender.get_latest_transaction_amount()
            assert latest_amount == TRANSFER_AMOUNT

        with allure.step("After transfer: recipient balance on the transactions page"):
            transactions_page_recipient.page.goto(f"{config.FRONTEND_URL}/transactions")
            expect(transactions_page_recipient.balance_amount).to_have_text(
                f"${recipient_tx_balance_before + TRANSFER_AMOUNT:.2f}"
            )
            recipient_tx_balance_after = transactions_page_recipient.get_balance()

        with allure.step("After transfer: recipient dashboard stats are updated"):
            dashboard_page_recipient.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page_recipient.balance_amount).to_have_text(f"${recipient_tx_balance_after:.2f}")
            recipient_dash_balance_after = dashboard_page_recipient.get_balance()
            recipient_dash_received_after = dashboard_page_recipient.get_total_received()
            recipient_dash_spent_after = dashboard_page_recipient.get_total_spent()
            recipient_dash_count_after = dashboard_page_recipient.get_transactions_count()

            assert recipient_dash_balance_after == recipient_tx_balance_before + TRANSFER_AMOUNT
            assert recipient_dash_received_after == recipient_dash_received_before + TRANSFER_AMOUNT
            assert recipient_dash_spent_after == recipient_dash_spent_before
            assert recipient_dash_count_after == 1

        with allure.step("After transfer: transfer is shown in the recipient dashboard history"):
            latest_amount = dashboard_page_recipient.get_latest_transaction_amount()
            assert latest_amount == TRANSFER_AMOUNT

    @pytest.mark.negative
    @allure.story("Transfer rejected: invalid input")
    @allure.title("Transfer with invalid amount: '{value}'")
    @pytest.mark.parametrize("value", ["0", "-100", "", " "])
    def test_transfer_invalid_amount(
        self, transactions_page_with_deposit: TransactionsPage, recipient_account: dict, value: str
    ) -> None:
        number_recipient_account = recipient_account["account_number"]
        transactions_page_with_deposit.open_transfer_confirm(value, "deposit 1", number_recipient_account)
        expect(transactions_page_with_deposit.transaction_error).to_be_visible()

    @pytest.mark.negative
    @allure.story("Transfer rejected: account not found")
    @allure.title("Transfer to a nonexistent account number")
    def test_transfer_recipient_not_found(self, transactions_page_with_deposit: TransactionsPage) -> None:
        transactions_page_with_deposit.confirm_send_transfer("50", "deposit 1", "123123")
        expect(transactions_page_with_deposit.transaction_error).to_be_visible()

    @pytest.mark.negative
    @allure.story("Transfer rejected: invalid input")
    @allure.title("Transfer with an empty account number")
    def test_transfer_recipient_empty(self, transactions_page_with_deposit: TransactionsPage) -> None:
        transactions_page_with_deposit.open_transfer_confirm("50", "deposit 1", "")
        expect(transactions_page_with_deposit.transaction_error).to_be_visible()

    @pytest.mark.negative
    @allure.story("Transfer rejected: insufficient funds")
    @allure.title("Transfer more than the balance")
    def test_transfer_insufficient_funds(
        self,
        transactions_page_with_deposit: TransactionsPage,
        recipient_account: dict,
        logged_in_page_recipient: Page,
        transactions_page_recipient: TransactionsPage,
    ) -> None:
        expect(transactions_page_with_deposit.balance_amount).not_to_have_text("$0.00")
        sender_amount_before = transactions_page_with_deposit.get_balance()
        number_recipient_account = recipient_account["account_number"]
        recipient_amount_before = transactions_page_recipient.get_balance()
        transactions_page_with_deposit.confirm_send_transfer("500", "deposit 1", number_recipient_account)
        expect(transactions_page_with_deposit.transaction_error).to_be_visible()

        assert transactions_page_with_deposit.get_balance() == sender_amount_before
        # reload: the recipient page does not refresh on its own after the sender's action
        transactions_page_recipient.page.reload()
        assert transactions_page_recipient.get_balance() == recipient_amount_before

    @allure.story("Transfer can be cancelled before confirmation")
    @allure.title("Cancel a transfer in the confirmation modal")
    def test_transfer_cancel_in_modal(
        self,
        transactions_page_with_deposit: TransactionsPage,
        recipient_account: dict,
        logged_in_page_recipient: Page,
        transactions_page_recipient: TransactionsPage,
    ) -> None:
        expect(transactions_page_with_deposit.balance_amount).not_to_have_text("$0.00")
        sender_amount_before = transactions_page_with_deposit.get_balance()
        number_recipient_account = recipient_account["account_number"]
        recipient_amount_before = transactions_page_recipient.get_balance()
        transactions_page_with_deposit.cancel_send_transfer("50", "deposit 1", number_recipient_account)
        sender_amount_after = transactions_page_with_deposit.get_balance()
        assert sender_amount_after == sender_amount_before

        # reload: the recipient page does not refresh on its own after the sender's action
        transactions_page_recipient.page.reload()
        recipient_amount_after = transactions_page_recipient.get_balance()
        assert recipient_amount_after == recipient_amount_before