from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page_title = page.get_by_test_id("page-title")
        self.no_orders_block = page.get_by_test_id("no-orders")
        self.browse_product_button = page.get_by_role("button", name="Browse Products")
        self.orders_list = page.get_by_test_id("orders-list")
        self.order_item = page.get_by_test_id("order-item")
        self.order_product_name = page.get_by_test_id("order-product-name")
        self.order_quantity = page.get_by_test_id("order-quantity")
        self.order_total_price = page.get_by_test_id("order-total-price")
        self.pay_order_button = page.get_by_test_id("pay-order-button")
        self.cancel_order_button = page.get_by_test_id("cancel-order-button")
        self.error_message = page.get_by_test_id("payment-error-message")
        self.success_message = page.get_by_test_id("payment-success-message")

    def browse_product(self) -> None:
        self.browse_product_button.click()

    def pay_order(self) -> None:
        self.pay_order_button.click()

    def cancel_order(self) -> None:
        self.cancel_order_button.click()
