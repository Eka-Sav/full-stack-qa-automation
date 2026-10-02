"""DB checks for products: created and deactivated products persisted after API calls."""

import allure
import pytest

from database.db_manager import DBManager

pytestmark = [allure.epic("Product Catalog"), pytest.mark.db]


@allure.feature("Product Creation")
class TestCreateProductDB:
    @allure.story("Product is created")
    def test_create_product_saved_in_db(self, created_product: dict, db: DBManager) -> None:
        product_in_db = db.get_product_by_id(created_product["id"])
        assert product_in_db is not None
        assert product_in_db["name"] == created_product["name"]
        assert product_in_db["description"] == created_product["description"]
        assert product_in_db["price"] == created_product["price"]
        assert product_in_db["category"] == created_product["category"]
        assert product_in_db["created_at"] is not None
        assert product_in_db["is_active"] == 1

    @allure.story("Product is created")
    def test_create_product_schema_in_db(self, created_product: dict, db: DBManager) -> None:
        product_schema_in_db = db.get_product_by_id(created_product["id"])
        assert isinstance(product_schema_in_db["id"], int)
        assert isinstance(product_schema_in_db["name"], str)
        assert isinstance(product_schema_in_db["description"], str)
        assert isinstance(product_schema_in_db["price"], float)
        assert isinstance(product_schema_in_db["category"], str)
        assert isinstance(product_schema_in_db["is_active"], int)


@allure.feature("Product Deactivation")
class TestDeactivateProductDB:
    @allure.story("Deactivated product is hidden from catalog")
    def test_deactivate_product_saved_in_db(self, deactivated_product: dict, db: DBManager) -> None:
        product_in_db = db.get_product_by_id(deactivated_product["id"])
        assert product_in_db is not None
        assert product_in_db["is_active"] == 0
