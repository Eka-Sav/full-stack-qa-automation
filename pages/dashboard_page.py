from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.account_balance = page.get_by_test_id("account-balance")
        self.balance_amount = page.get_by_test_id("balance-amount")
        self.transaction_list = page.get_by_test_id("transaction-list")
        self.no_transactions = page.get_by_test_id("no-transactions")
        self.transaction_item = page.get_by_test_id("transaction-item")
        self.transaction_type = page.get_by_test_id("transaction-type")
        self.transaction_amount = page.get_by_test_id("transaction-amount")
        self.stat_total_received = page.get_by_test_id("stat-total-received")
        self.stat_total_received_value = page.get_by_test_id("stat-total-received-value")
        self.stat_total_spent = page.get_by_test_id("stat-total-spent")
        self.stat_total_spent_value = page.get_by_test_id("stat-total-spent-value")
        self.stat_transactions = page.get_by_test_id("stat-transactions")
        self.stat_transactions_value = page.get_by_test_id("stat-transactions-value")

    def get_balance(self) -> float:
        return self._parse_amount(self.balance_amount.inner_text())

    def get_total_received(self) -> float:
        return self._parse_amount(self.stat_total_received_value.inner_text())

    def get_total_spent(self) -> float:
        return self._parse_amount(self.stat_total_spent_value.inner_text())

    def get_transactions_count(self) -> int:
        return int(self.stat_transactions_value.inner_text())

    def get_latest_transaction(self) -> Locator:
        # the list is sorted newest first (created_at desc)
        return self.transaction_item.first

    def get_latest_transaction_amount(self) -> float:
        amount = self.get_latest_transaction().get_by_test_id("transaction-amount")
        return self._parse_amount(amount.inner_text())

