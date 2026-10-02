from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class OrdersPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page_title = page.get_by_test_id("page-title")
        self.no_orders_block = page.get_by_test_id("no-orders")
        self.browse_product_button = page.get_by_role("button", name="Browse Products")
        self.orders_list = page.get_by_test_id("orders-list")
        self.order_item = page.get_by_test_id("order-item")
        self.order_product_name = page.get_by_test_id("order-product-name")
        self.order_status = page.get_by_test_id("order-status")
        self.order_quantity = page.get_by_test_id("order-quantity")
        self.order_total_price = page.get_by_test_id("order-total-price")

    def browse_product(self) -> None:
        self.browse_product_button.click()

    def get_filter(self, status: str) -> Locator:
        return self.page.get_by_test_id(f"filter-{status}")

    def select_status_filter(self, order_status: str) -> None:
        self.get_filter(order_status).click()

    def get_order_item_by_id(self, order_id: int) -> Locator:
        return self.order_item.filter(has=self.page.get_by_text(f"Order #{order_id}", exact=True))
