"""UI tests for the orders page: order list and status filter."""

import allure
import pytest
from playwright.sync_api import expect

from pages.orders_page import OrdersPage

pytestmark = [allure.epic("Cart & Orders"), pytest.mark.ui]


@allure.feature("Order History")
class TestOrdersPage:
    @allure.story("Orders are filtered by status")
    @allure.title("Filter orders by status: {status}")
    @pytest.mark.parametrize("status", ["paid", "cancelled", "all"])
    def test_order_filter(self, paid_order: dict, cancelled_order: dict, orders_page: OrdersPage, status: str) -> None:
        orders_page.select_status_filter(status)
        if status != "all":
            for s in orders_page.order_status.all():
                expect(s).to_contain_text(status.capitalize())
        else:
            assert orders_page.order_item.count() > 0

    @allure.story("User orders are listed and retrievable")
    @allure.title("Paid order is listed")
    def test_order_paid(self, created_products: list[dict], paid_order: dict, orders_page: OrdersPage) -> None:
        order_id = paid_order["id"]
        item = orders_page.get_order_item_by_id(order_id)
        expect(item.get_by_test_id("order-product-name")).to_contain_text(f"Order #{order_id}")
        expect(item.get_by_test_id("order-status")).to_contain_text("Paid")

    @allure.story("User orders are listed and retrievable")
    @allure.title("Cancelled order is listed")
    def test_order_cancelled(
        self, created_products: list[dict], cancelled_order: dict, orders_page: OrdersPage
    ) -> None:
        order_id = cancelled_order["id"]
        item = orders_page.get_order_item_by_id(order_id)
        expect(item.get_by_test_id("order-product-name")).to_contain_text(f"Order #{order_id}")
        expect(item.get_by_test_id("order-status")).to_contain_text("Cancelled")

    @allure.story("User orders are listed and retrievable")
    @allure.title("Order shows its quantity")
    def test_order_quantity(self, created_products: list[dict], confirmed_order: dict, orders_page: OrdersPage) -> None:
        order_id = confirmed_order["id"]
        item = orders_page.get_order_item_by_id(order_id)
        expect(item.get_by_test_id("order-quantity")).to_contain_text(str(confirmed_order["quantity"]))

    @allure.story("User orders are listed and retrievable")
    @allure.title("Order shows its total price")
    def test_order_price(self, created_products: list[dict], confirmed_order: dict, orders_page: OrdersPage) -> None:
        order_id = confirmed_order["id"]
        item = orders_page.get_order_item_by_id(order_id)
        expect(item.get_by_test_id("order-total-price")).to_contain_text(str(confirmed_order["total_price"]))
