"""UI tests for the products page: listing, search, sorting and the order form."""

import uuid
from typing import Callable

import allure
import pytest
from playwright.sync_api import expect

from pages.products_page import ProductsPage

# epic is set per class: TestOrderForm belongs to Cart & Orders, not Product Catalog
pytestmark = [pytest.mark.ui]


@allure.epic("Product Catalog")
class TestProductsPage:
    @allure.feature("Product Listing")
    @allure.story("Products are listed and retrievable")
    @allure.title("Products are displayed on the page")
    def test_products_displayed(self, products_page: ProductsPage, created_product: dict) -> None:
        products_page.page.reload()
        expect(products_page.product_item.first).to_be_visible()

    @allure.feature("Search, Filtering & Sorting")
    @allure.story("Products are searched and filtered by category")
    @allure.title("Search a product by name")
    def test_search_product(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        name = created_products[0]["name"]
        products_page.page.reload()
        products_page.search_product(name)
        expect(products_page.product_name.first).to_be_visible()

    @allure.feature("Search, Filtering & Sorting")
    @allure.story("Products are sorted by price")
    @allure.title("Sort products by price ascending")
    def test_sort_product_asc(self, products_page: ProductsPage, product_factory: Callable[..., dict]) -> None:
        # more products than page_size, so sorting is checked across pages
        prices = [10, 50, 5, 100, 25, 75, 30, 60, 15, 90, 40, 20]
        for p in prices:
            product_factory(price=p)
        products_page.sort_product("asc")
        displayed_prices = [float(text.replace("$", "")) for text in products_page.product_price.all_inner_texts()]
        assert displayed_prices == sorted(displayed_prices)

    @allure.feature("Search, Filtering & Sorting")
    @allure.story("Products are sorted by price")
    @allure.title("Sort products by price descending")
    def test_sort_product_desc(self, products_page: ProductsPage, product_factory: Callable[..., dict]) -> None:
        prices = [10, 50, 5, 100, 25, 75, 30, 60, 15, 90, 40, 20]
        for p in prices:
            product_factory(price=p)
        products_page.sort_product("desc")
        displayed_prices = [float(text.replace("$", "")) for text in products_page.product_price.all_inner_texts()]
        assert displayed_prices == sorted(displayed_prices, reverse=True)

    @allure.feature("Search, Filtering & Sorting")
    @allure.story("Products are searched and filtered by category")
    @allure.title("Filter products by category")
    def test_get_product_category(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        products_page.page.reload()
        products_page.apply_filter_by_category("service")
        for category in products_page.product_category.all():
            expect(category).to_contain_text("service")


@allure.epic("Product Catalog")
@allure.feature("Product Listing")
class TestProductCard:
    @allure.story("Products are listed and retrievable")
    @allure.title("Product card shows name and price")
    def test_product_card(self, products_page: ProductsPage, product_factory: Callable[..., dict]) -> None:
        target_product = product_factory(name=f"Test product {uuid.uuid4().hex[:8]}", price="1000")
        name = target_product["name"]
        products_page.page.reload()
        products_page.search_product(name)
        card = products_page.get_product_card(target_product["id"])

        expect(card).to_be_visible(timeout=10000)
        expect(card.get_by_test_id("product-name")).to_have_text(target_product["name"])
        expect(card.get_by_test_id("product-price")).to_have_text(f"${target_product['price']:.2f}")


@allure.epic("Cart & Orders")
@allure.feature("Order Creation")
class TestOrderForm:
    @allure.story("Order form can be cancelled")
    @allure.title("Cancel the order form")
    def test_order_form_cancel(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        products_page.add_product_cancel()
        expect(products_page.order_form).to_be_hidden()

    @allure.story("Order is created")
    @allure.title("Confirm the order form")
    def test_order_form_confirm(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        products_page.add_product_confirm(quantity="1")
        expect(products_page.order_success_message).to_be_visible()

    @pytest.mark.negative
    @allure.story("Order creation rejected: invalid input")
    @allure.title("Order form rejects zero quantity")
    def test_order_form_invalid_quantity(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        products_page.add_product_confirm("0")
        expect(products_page.order_error_message).to_be_visible()

    @allure.story("Order is created")
    @allure.title("Buy button opens the order form")
    def test_order_form_opens(self, products_page: ProductsPage, created_products: list[dict]) -> None:
        products_page.buy_button.first.click()
        expect(products_page.order_form).to_be_visible()
