from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class ProductsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.page_title = page.get_by_test_id("page-title")
        self.search_input = page.get_by_test_id("search-input")
        self.sort_select = page.get_by_test_id("sort-select")
        self.category_filter = page.get_by_test_id("category-filter")
        self.no_products = page.get_by_test_id("no-products")
        self.products_list = page.get_by_test_id("products-list")
        self.product_item = page.locator('[data-testid^="product-item-"]')
        self.product_name = page.get_by_test_id("product-name")
        self.product_price = page.get_by_test_id("product-price")
        self.product_category = page.get_by_test_id("product-category")
        self.buy_button = page.get_by_test_id("buy-button")
        self.order_form = page.get_by_test_id("order-form")
        self.order_form_product_name = page.get_by_test_id("order-form-product-name")
        self.quantity_input = page.get_by_test_id("quantity-input")
        self.order_total_preview = page.get_by_test_id("order-total-preview")
        self.confirm_order_button = page.get_by_test_id("confirm-order-button")
        self.cancel_form_button = page.get_by_test_id("cancel-form-button")
        self.order_error_message = page.get_by_test_id("order-error-message")
        self.order_success_message = page.get_by_test_id("order-success-message")

    def get_product_card(self, product_id: int) -> Locator:
        return self.page.get_by_test_id(f"product-item-{product_id}")

    def search_product(self, name: str) -> None:
        self.search_input.fill(name)

    def sort_product(self, sort: str) -> None:
        self.sort_select.select_option(sort)

    def find_category_filter_button(self, category: str) -> Locator:
        return self.page.get_by_test_id(f"filter-{category}")

    def apply_filter_by_category(self, product_category: str) -> None:
        category = self.find_category_filter_button(product_category)
        category.click()

    def add_product_confirm(self, quantity: str) -> None:
        self.buy_button.first.click()
        self.quantity_input.fill(quantity)
        self.confirm_order_button.click()

    def add_product_cancel(self) -> None:
        self.buy_button.first.click()
        self.cancel_form_button.click()

    def get_displayed_prices(self) -> list[float]:
        return [self._parse_amount(text) for text in self.product_price.all_inner_texts()]
