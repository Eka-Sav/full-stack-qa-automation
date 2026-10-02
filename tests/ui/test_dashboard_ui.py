"""UI tests for the dashboard: balance, transaction list and stats."""

import allure
import pytest
from playwright.sync_api import expect

from api.api_client import APIClient
from api.endpoints import Endpoints
from pages.dashboard_page import DashboardPage

pytestmark = [allure.epic("Transactions & Balance"), pytest.mark.ui]


@allure.feature("Dashboard")
class TestDashboardBalance:
    @allure.story("Dashboard balance matches account")
    @allure.title("Balance matches the account after a deposit")
    def test_dashboard_balance_matches_account_deposit(
        self,
        created_user: dict,
        dashboard_page: DashboardPage,
        created_transaction_deposit: dict,
        user_account: dict,
        api_client: APIClient,
    ) -> None:
        dashboard_page.page.reload()
        response = api_client.get(Endpoints.accounts(created_user["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_account = response.json()[0]
        dashboard_balance = dashboard_page.get_balance()
        assert dashboard_balance == new_account["balance"]

    @allure.story("Dashboard balance matches account")
    @allure.title("Balance matches the account after a transfer")
    def test_dashboard_balance_matches_account_transfer(
        self,
        created_user: dict,
        dashboard_page: DashboardPage,
        created_transfer: dict,
        user_account: dict,
        api_client: APIClient,
    ) -> None:
        dashboard_page.page.reload()
        response = api_client.get(Endpoints.accounts(created_user["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_account = response.json()[0]
        dashboard_balance = dashboard_page.get_balance()
        assert dashboard_balance == new_account["balance"]

    @allure.story("Dashboard balance matches account")
    @allure.title("Balance matches the account after an order payment")
    def test_dashboard_balance_matches_account_order(
        self,
        created_user: dict,
        dashboard_page: DashboardPage,
        paid_order: dict,
        user_account: dict,
        api_client: APIClient,
    ) -> None:
        dashboard_page.page.reload()
        response = api_client.get(Endpoints.accounts(created_user["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_account = response.json()[0]
        dashboard_balance = dashboard_page.get_balance()
        assert dashboard_balance == new_account["balance"]

    @allure.story("Dashboard shows empty state for new account")
    @allure.title("New account shows 'No transactions yet'")
    def test_dashboard_no_transactions_state(self, dashboard_page: DashboardPage) -> None:
        expect(dashboard_page.no_transactions).to_be_visible()


@allure.feature("Dashboard")
class TestDashboardTransactionTypesDisplay:
    @allure.story("Dashboard shows all transaction types")
    @allure.title("Deposit is listed with '+' and green amount")
    def test_dashboard_shows_deposit_transaction(
        self, dashboard_page: DashboardPage, created_transaction_deposit: dict
    ) -> None:
        dashboard_page.page.reload()
        amount = created_transaction_deposit["amount"]
        tx_type = created_transaction_deposit["transaction_type"]

        transaction_item = dashboard_page.get_latest_transaction()
        transaction_type = transaction_item.get_by_test_id("transaction-type")
        transaction_amount = transaction_item.get_by_test_id("transaction-amount")

        expect(transaction_item).to_be_visible()
        expect(transaction_type).to_contain_text(tx_type)
        expect(transaction_amount).to_have_css("color", "rgb(16, 185, 129)")
        expect(transaction_amount).to_contain_text(f"+${amount}")

    @allure.story("Dashboard shows all transaction types")
    @allure.title("Outgoing transfer is listed with '-' and red amount")
    def test_dashboard_shows_transfer_transaction(self, dashboard_page: DashboardPage, created_transfer: dict) -> None:
        dashboard_page.page.reload()
        amount = created_transfer["amount"]
        tx_type = created_transfer["transaction_type"]

        transaction_item = dashboard_page.get_latest_transaction()
        transaction_type = transaction_item.get_by_test_id("transaction-type")
        transaction_amount = transaction_item.get_by_test_id("transaction-amount")

        expect(transaction_item).to_be_visible()
        expect(transaction_type).to_contain_text(tx_type)
        expect(transaction_amount).to_have_css("color", "rgb(244, 63, 94)")
        expect(transaction_amount).to_contain_text(f"-${amount}")

    @allure.story("Dashboard shows all transaction types")
    @allure.title("Payment is listed with '-' and red amount")
    def test_dashboard_shows_payment_transaction(
        self, dashboard_page: DashboardPage, paid_order: dict, created_order: dict
    ) -> None:
        dashboard_page.page.reload()
        amount = created_order["total_price"]

        transaction_item = dashboard_page.get_latest_transaction()
        transaction_type = transaction_item.get_by_test_id("transaction-type")
        transaction_amount = transaction_item.get_by_test_id("transaction-amount")

        expect(transaction_item).to_be_visible()
        expect(transaction_type).to_contain_text("payment")
        expect(transaction_amount).to_have_css("color", "rgb(244, 63, 94)")
        expect(transaction_amount).to_contain_text(f"-${amount}")


@allure.feature("Dashboard")
class TestDashboardStatus:
    @allure.story("Dashboard stats match transactions")
    @allure.title("Total Received sums incoming transactions")
    def test_dashboard_total_received_status(
        self,
        dashboard_page: DashboardPage,
        created_transaction_deposit: dict,
        created_transfer: dict,
        paid_order: dict,
        user_account: dict,
        recipient_account: dict,
        api_client: APIClient,
    ) -> None:
        recipient_deposit = 50.0
        incoming_transfer = 20.0

        # the recipient needs funds before sending money back to the current user
        deposit_response = api_client.post(
            Endpoints.TRANSACTIONS,
            json={
                "account_id": recipient_account["id"],
                "amount": recipient_deposit,
                "transaction_type": "deposit",
                "description": "recipient deposit",
            },
        )
        assert deposit_response.status_code == 201, f"Unexpected response: {deposit_response.text}"

        transfer_response = api_client.post(
            Endpoints.TRANSFERS,
            json={
                "from_account_id": recipient_account["id"],
                "to_account_id": user_account["id"],
                "amount": incoming_transfer,
                "description": "incoming transfer",
            },
        )
        assert transfer_response.status_code == 201, f"Unexpected response: {transfer_response.text}"
        dashboard_page.page.reload()
        # outgoing transfer and payment must not be counted as received
        received_amount = created_transaction_deposit["amount"] + incoming_transfer
        expect(dashboard_page.stat_total_received).to_contain_text(f"Total Received+${received_amount:.2f}")

    @allure.story("Dashboard stats match transactions")
    @allure.title("Total Spent sums outgoing transactions")
    def test_dashboard_total_spent_status(
        self,
        dashboard_page: DashboardPage,
        created_transaction_deposit: dict,
        created_transfer: dict,
        paid_order: dict,
        created_order: dict,
    ) -> None:
        dashboard_page.page.reload()
        expected_spent = created_transfer["amount"] + created_order["total_price"]
        expect(dashboard_page.stat_total_spent).to_contain_text(f"-${expected_spent}")

    @allure.story("Dashboard stats match transactions")
    @allure.title("Transactions count matches the account transactions")
    def test_dashboard_transactions_count_status(
        self,
        dashboard_page: DashboardPage,
        created_transaction_deposit: dict,
        created_transfer: dict,
        paid_order: dict,
        created_order: dict,
        api_client: APIClient,
        user_account: dict,
    ) -> None:
        dashboard_page.page.reload()
        response = api_client.get(Endpoints.transaction_by_account(user_account["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        transactions = response.json()
        expect(dashboard_page.stat_transactions).to_contain_text(str(len(transactions)))
