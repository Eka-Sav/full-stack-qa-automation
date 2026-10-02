from playwright.sync_api import Page

from pages.base_page import BasePage


class TransactionsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page_title = page.get_by_test_id("page-title")
        self.balance_amount = page.get_by_test_id("balance-amount")
        self.mode_switcher = page.get_by_test_id("mode-switcher")
        self.mode_deposit = page.get_by_test_id("mode-deposit")
        self.mode_transfer = page.get_by_test_id("mode-transfer")
        self.recipient_input = page.get_by_test_id("recipient-input")
        self.amount_input = page.get_by_test_id("amount-input")
        self.description_input = page.get_by_test_id("description-input")
        self.submit_button = page.get_by_test_id("submit-button")

        self.confirm_modal_overlay = page.get_by_test_id("confirm-modal-overlay")
        self.confirm_modal = page.get_by_test_id("confirm-modal")
        self.confirm_recipient = page.get_by_test_id("confirm-recipient")
        self.confirm_amount = page.get_by_test_id("confirm-amount")
        self.confirm_description = page.get_by_test_id("confirm-description")
        self.transfer_cancel_button = page.get_by_test_id("confirm-cancel-button")
        self.transfer_submit_button = page.get_by_test_id("confirm-submit-button")

        self.transaction_error = page.get_by_test_id("transaction-error")
        self.transaction_success = page.get_by_test_id("transaction-success")

    def confirm_send_deposit(self, amount: str, description: str) -> None:
        self.mode_deposit.click()
        self.amount_input.fill(amount)
        self.description_input.fill(description)
        self.submit_button.click()

    def open_transfer_confirm(self, amount: str, description: str, account_number: str) -> None:
        self.mode_transfer.click()
        self.recipient_input.fill(account_number)
        self.amount_input.fill(amount)
        self.description_input.fill(description)
        self.submit_button.click()

    def confirm_send_transfer(self, amount: str, description: str, account_number: str) -> None:
        self.open_transfer_confirm(amount, description, account_number)
        self.transfer_submit_button.click()

    def cancel_send_transfer(self, amount: str, description: str, account_number: str) -> None:
        self.open_transfer_confirm(amount, description, account_number)
        self.transfer_cancel_button.click()

    def get_balance(self) -> float:
        return self._parse_amount(self.balance_amount.inner_text())


