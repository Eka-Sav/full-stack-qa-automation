"""UI tests for the cart page: paying, cancelling and viewing orders."""

import re

import allure
import pytest
from playwright.sync_api import expect

from api.api_client import APIClient
from api.endpoints import Endpoints
from pages.cart_page import CartPage

pytestmark = [allure.epic("Cart & Orders"), pytest.mark.ui]


class TestCartPage:
    @allure.feature("Order Payment")
    @allure.story("Confirmed order is paid and balance decreases")
    @allure.title("Pay an order from the cart")
    def test_cart_pay_product(self, cart_page_via_api: CartPage, created_transaction_deposit: dict) -> None:
        cart_page_via_api.pay_order()
        expect(cart_page_via_api.success_message).to_contain_text("paid")

    @allure.feature("Order Cancellation")
    @allure.story("Order is cancelled")
    @allure.title("Cancel an order from the cart")
    def test_cart_cancel_product(self, cart_page_via_api: CartPage) -> None:
        cart_page_via_api.cancel_order()
        expect(cart_page_via_api.success_message).to_contain_text("cancelled.")

    @allure.feature("Cart")
    @allure.story("Empty cart links to catalog")
    @allure.title("Empty cart leads to the products page")
    def test_cart_browse_product(self, cart_page_empty: CartPage) -> None:
        cart_page_empty.browse_product()
        cart_page_empty.page.wait_for_url(re.compile("products"))

    @allure.feature("Cart")
    @allure.story("Ordered product appears in cart")
    @allure.title("Ordered product is shown in the cart")
    def test_product_appears_in_cart(self, cart_page: CartPage, created_product: dict) -> None:
        expect(cart_page.order_item).to_be_visible()

    @allure.feature("Order Payment")
    @allure.story("Payment rejected: insufficient funds")
    @allure.title("Pay an order from the cart with insufficient funds")
    @pytest.mark.negative
    def test_cart_pay_insufficient_funds(self, cart_page_via_api: CartPage) -> None:
        cart_page_via_api.pay_order()
        expect(cart_page_via_api.error_message).to_contain_text("Insufficient funds")

    @allure.feature("Order Payment")
    @allure.story("Payment rejected: insufficient funds")
    @allure.title("Failed payment does not confirm the order")
    @pytest.mark.negative
    @pytest.mark.xfail(
        reason="Known bug: cart confirms the order before payment; confirm is not rolled back when payment fails"
    )
    def test_cart_failed_payment_keeps_order_pending(
        self, cart_page_via_api: CartPage, created_order: dict, api_client: APIClient
    ) -> None:
        cart_page_via_api.pay_order()
        # wait for the error so both requests (confirm and pay) have finished before reading the status
        expect(cart_page_via_api.error_message).to_contain_text("Insufficient funds")

        response = api_client.get(Endpoints.order(created_order["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        assert response.json()["status"] == "pending"
