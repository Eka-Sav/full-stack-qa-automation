"""API tests for /products: create, list, sort, get, delete"""

from typing import Callable

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints
from data.products import PRODUCTS

pytestmark = [
    allure.epic("Product Catalog"),
    pytest.mark.api,
]


@allure.feature("Product Creation")
class TestCreateProducts:
    @allure.story("Product is created")
    @pytest.mark.smoke
    @pytest.mark.parametrize("product_data", PRODUCTS)
    def test_create_product_returns_201(self, api_client: APIClient, product_data: dict) -> None:
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        new_product = response.json()
        assert new_product is not None
        assert new_product["id"] is not None
        assert new_product["name"] == product_data["name"]
        assert new_product["description"] == product_data["description"]
        assert new_product["price"] == product_data["price"]
        assert new_product["category"] == product_data["category"]
        assert new_product["is_active"] is not None

    @allure.story("Product is created")
    def test_created_product_response_schema(self, created_product: dict) -> None:
        assert isinstance(created_product["id"], int)
        assert isinstance(created_product["name"], str)
        assert isinstance(created_product["description"], str)
        assert isinstance(created_product["price"], float)
        assert isinstance(created_product["category"], str)
        assert isinstance(created_product["is_active"], int)

    @allure.story("Product is created")
    @pytest.mark.parametrize(
        "name",
        [
            "商品 Продукт منتج",
            "Café Münchener Straße",
        ],
    )
    def test_create_product_with_international_name_returns_201(
        self, api_client: APIClient, product_data: dict, name: str
    ) -> None:
        product_data["name"] = name
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        assert response.json()["name"] == name

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("name", "A"), ("name", "")])
    def test_create_product_short_name_returns_400(
        self, api_client: APIClient, product_data: dict, field: str, value: str
    ) -> None:
        product_data[field] = value
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Product name must be at least 2 characters" in response.json()["detail"]

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("price", 0), ("price", -1)])
    def test_create_product_invalid_value_price_returns_400(
        self, api_client: APIClient, product_data: dict, field: str, value: int
    ) -> None:
        product_data[field] = value
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Price must be positive" in response.json()["detail"]

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_invalid_type_name_returns_422(self, api_client: APIClient, product_data: dict) -> None:
        product_data["name"] = 123
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_invalid_type_price_returns_422(self, api_client: APIClient, product_data: dict) -> None:
        product_data["price"] = {"value": 10}
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_invalid_type_description_returns_422(
        self, api_client: APIClient, product_data: dict
    ) -> None:
        product_data["description"] = {"value": 10}
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_invalid_type_category_returns_422(self, api_client: APIClient, product_data: dict) -> None:
        product_data["category"] = {"value": 10}
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_missing_name_returns_422(self, api_client: APIClient, product_data: dict) -> None:
        product_data.pop("name")
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Product creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_product_missing_price_returns_422(self, api_client: APIClient, product_data: dict) -> None:
        product_data.pop("price")
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Product Listing")
class TestGetProductsList:
    @allure.story("Products are listed and retrievable")
    @pytest.mark.smoke
    def test_get_products_list_returns_200(self, api_client: APIClient, created_product: dict) -> None:
        response = api_client.get(Endpoints.PRODUCTS)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0
        ids = [p["id"] for p in products]
        assert created_product["id"] in ids

    @allure.story("Products are listed and retrievable")
    def test_get_products_list_response_schema(self, api_client: APIClient, created_product: dict) -> None:
        response = api_client.get(Endpoints.PRODUCTS)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        product = response.json()[0]
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["description"], str)
        assert isinstance(product["price"], float)
        assert isinstance(product["category"], str)


@allure.feature("Search, Filtering & Sorting")
class TestProductsSortAPI:
    @allure.story("Products are sorted by price")
    def test_sort_products_by_price_asc(self, api_client: APIClient, product_factory: Callable[..., dict]) -> None:
        prices = [10, 50, 5, 100, 25, 75, 30, 60, 15, 90, 40, 20]
        for p in prices:
            product_factory(price=p)

        response = api_client.get(Endpoints.PRODUCTS, params={"sort_by": "price", "order": "asc"})
        assert response.status_code == 200, f"Unexpected response: {response.text}"

        returned_prices = [item["price"] for item in response.json()]
        assert returned_prices == sorted(returned_prices)

    @allure.story("Products are sorted by price")
    def test_sort_products_by_price_desc(self, api_client: APIClient, product_factory: Callable[..., dict]) -> None:
        prices = [10, 50, 5, 100, 25, 75, 30, 60, 15, 90, 40, 20]
        for p in prices:
            product_factory(price=p)

        response = api_client.get(Endpoints.PRODUCTS, params={"sort_by": "price", "order": "desc"})
        assert response.status_code == 200, f"Unexpected response: {response.text}"

        returned_prices = [item["price"] for item in response.json()]
        assert returned_prices == sorted(returned_prices, reverse=True)

    @allure.story("Sorting rejected: invalid parameters")
    @pytest.mark.negative
    def test_sort_products_invalid_value_sort_by_returns_400(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.PRODUCTS, params={"sort_by": "banana"})
        assert response.status_code == 400, f"Unexpected response: {response.text}"

    @allure.story("Sorting rejected: invalid parameters")
    @pytest.mark.negative
    def test_sort_products_invalid_value_order_returns_400(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.PRODUCTS, params={"sort_by": "price", "order": "sideways"})
        assert response.status_code == 400, f"Unexpected response: {response.text}"


@allure.feature("Product Listing")
class TestGetProductById:
    @allure.story("Products are listed and retrievable")
    @pytest.mark.smoke
    def test_get_product_returns_200(self, api_client: APIClient, created_product: dict) -> None:
        response = api_client.get(Endpoints.product(created_product["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_product = response.json()
        assert new_product is not None
        assert new_product["name"] == created_product["name"]
        assert new_product["description"] == created_product["description"]
        assert new_product["price"] == created_product["price"]
        assert new_product["category"] == created_product["category"]
        assert new_product["is_active"] is not None
        assert new_product["is_active"] == 1

    @allure.story("Products are listed and retrievable")
    def test_get_product_response_schema(self, api_client: APIClient, created_product: dict) -> None:
        response = api_client.get(Endpoints.product(created_product["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        product = response.json()
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["description"], str)
        assert isinstance(product["price"], float)
        assert isinstance(product["category"], str)
        assert isinstance(product["is_active"], int)

    @allure.story("Product lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_product_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.product(99999999))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Product not found" in response.json()["detail"]["error_message"]

    @allure.story("Product lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_product_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.product("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Product Deactivation")
class TestDeleteProduct:
    @allure.story("Deactivated product is hidden from catalog")
    @pytest.mark.smoke
    def test_delete_product_returns_204(self, api_client: APIClient, created_product: dict) -> None:
        response = api_client.delete(Endpoints.product(created_product["id"]))
        assert response.status_code == 204, f"Unexpected response: {response.text}"

    @allure.story("Deactivated product is hidden from catalog")
    def test_deactivate_product_not_in_list(self, api_client: APIClient, deactivated_product: dict) -> None:
        response = api_client.get(Endpoints.PRODUCTS)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        products = response.json()
        ids = [p["id"] for p in products]
        assert deactivated_product["id"] not in ids

    @allure.story("Deactivation rejected: not found or invalid id")
    @pytest.mark.negative
    def test_delete_product_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.delete(Endpoints.product(12312313))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Product not found" in response.json()["detail"]["error_message"]

    @allure.story("Deactivation rejected: not found or invalid id")
    @pytest.mark.negative
    def test_delete_product_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.delete(Endpoints.product("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )
