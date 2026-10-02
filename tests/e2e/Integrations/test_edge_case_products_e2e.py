"""E2E integration: product creation with AI-generated edge-case data is rejected."""

import json

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints

pytestmark = [allure.epic("Product Catalog"), pytest.mark.integration]

with open("data/ai_edge_case_products_data.json", "r", encoding="utf-8") as f:
    EDGE_CASE_PRODUCTS = json.load(f)

EXPECTED_STATUS = {
    "name_long": 400,  # name longer than 50 characters
    "name_emoji": 400,  # blocked by NAME_PATTERN
    "name_injection": 400,  # blocked by NAME_PATTERN
    "name_digits_only": 400,  # digits-only check
    "name_whitespace_only": 400,  # known bug: returns 201
    "description_empty": 400,  # known bug: returns 201
    "description_null": 400,  # known bug: returns 201
    "description_long": 400,  # known bug: returns 201
    "description_injection": 400,  # known bug: returns 201, security issue
    "category_invalid": 422,  # CategoryEnum
    "category_wrong_case": 422,  # CategoryEnum is case-sensitive
}

# xfail documents a bug the test has already caught with an honest red run, it is not a way to hide one
KNOWN_BUGS = {
    "name_whitespace_only",
    "description_empty",
    "description_null",
    "description_long",
    "description_injection",
}

test_params = []
for product in EDGE_CASE_PRODUCTS:
    if product["id"] in KNOWN_BUGS:
        test_params.append(
            pytest.param(product, marks=pytest.mark.xfail(reason="known bug, not fixed"), id=product["id"])
        )
    else:
        test_params.append(pytest.param(product, id=product["id"]))


@allure.feature("Product Creation")
class TestCreateEdgeCaseProducts:
    @pytest.mark.negative
    @allure.story("Product creation rejected: edge-case input (AI-generated)")
    @allure.title("Create a product with AI-generated edge-case data")
    @pytest.mark.parametrize("product_data", test_params)
    def test_create_product_edge_case(self, api_client: APIClient, product_data: dict) -> None:
        expected_status = EXPECTED_STATUS[product_data["id"]]
        response = api_client.post(Endpoints.PRODUCTS, json=product_data)
        assert response.status_code == expected_status, f"Unexpected response: {response.text}"
