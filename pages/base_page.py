from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.dashboard_button = page.get_by_role("button", name="Dashboard")
        self.products_button = page.get_by_role("button", name="Products")
        self.cart_button = page.get_by_role("button", name="Cart")
        self.orders_button = page.get_by_role("button", name="Orders")
        self.logout_button = page.get_by_test_id("logout-button")

    def navigate(self, url: str) -> None:
        self.page.goto(url)

    def dashboard(self) -> None:
        self.dashboard_button.click()

    def products(self) -> None:
        self.products_button.click()

    def cart(self) -> None:
        self.cart_button.click()

    def orders(self) -> None:
        self.orders_button.click()

    def logout(self) -> None:
        self.logout_button.click()

    @staticmethod
    def _parse_amount(text: str) -> float:
        # amounts are rendered with a sign and currency, e.g. "+$100.00"
        return float(text.replace("-", "").replace("$", "").replace("+", ""))
