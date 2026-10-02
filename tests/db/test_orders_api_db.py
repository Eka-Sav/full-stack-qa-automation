"""DB checks for orders: status changes and payment transactions persisted after API calls."""

import allure
import pytest

from database.db_manager import DBManager

pytestmark = [allure.epic("Cart & Orders"), pytest.mark.db]


@allure.feature("Order Creation")
class TestCreateOrderDB:
    @allure.story("Order is created")
    def test_created_order_saved_in_db(self, created_order: dict, db: DBManager) -> None:
        order_in_db = db.get_order_by_id(created_order["id"])
        assert order_in_db is not None
        assert order_in_db["id"] == created_order["id"]
        assert order_in_db["user_id"] == created_order["user_id"]
        assert order_in_db["product_id"] == created_order["product_id"]
        assert order_in_db["quantity"] == created_order["quantity"]
        assert order_in_db["total_price"] == created_order["total_price"]
        assert order_in_db["status"] == "pending"
        assert order_in_db["created_at"] is not None

    @allure.story("Order is created")
    def test_created_order_schema_in_db(self, created_order: dict, db: DBManager) -> None:
        order_schema_in_db = db.get_order_by_id(created_order["id"])
        assert isinstance(order_schema_in_db["id"], int)
        assert isinstance(order_schema_in_db["user_id"], int)
        assert isinstance(order_schema_in_db["product_id"], int)
        assert isinstance(order_schema_in_db["quantity"], int)
        assert isinstance(order_schema_in_db["total_price"], float)
        assert isinstance(order_schema_in_db["status"], str)


@allure.feature("Order Cancellation")
class TestCancelOrderStatusDB:
    @allure.story("Order is cancelled")
    def test_cancel_order_saved_in_db(self, cancelled_order: dict, db: DBManager) -> None:
        order_in_db = db.get_order_by_id(cancelled_order["id"])
        assert order_in_db is not None
        assert order_in_db["status"] == "cancelled"


@allure.feature("Order Confirmation")
class TestConfirmOrderStatusDB:
    @allure.story("Pending order is confirmed")
    def test_confirm_order_saved_in_db(self, confirmed_order: dict, db: DBManager) -> None:
        order_in_db = db.get_order_by_id(confirmed_order["id"])
        assert order_in_db is not None
        assert order_in_db["status"] == "confirmed"


@allure.feature("Order History")
class TestCountOrdersForUserDB:
    @allure.story("User orders are listed and retrievable")
    def test_count_orders_for_user_saved_in_db(self, created_order: dict, db: DBManager) -> None:
        order_in_db = db.count_orders_for_user(created_order["user_id"])
        assert order_in_db == 1


@allure.feature("Order Payment")
class TestPayOrderStatusDB:
    @allure.story("Confirmed order is paid and balance decreases")
    def test_pay_order_saved_in_db(self, paid_order: dict, db: DBManager) -> None:
        order_in_db = db.get_order_by_id(paid_order["id"])
        assert order_in_db is not None
        assert order_in_db["status"] == "paid"


@allure.feature("Order Payment")
class TestCreateTransactionPaymentDB:
    @allure.story("Confirmed order is paid and balance decreases")
    def test_created_transaction_payment_saved_in_db(self, paid_order: dict, user_account: dict, db: DBManager) -> None:
        payment_in_db = db.get_transaction_by_id(paid_order["transaction_id"])
        assert payment_in_db is not None
        assert payment_in_db["id"] == paid_order["transaction_id"]
        assert payment_in_db["account_id"] == user_account["id"]
        assert payment_in_db["amount"] == paid_order["total_price"]
        assert payment_in_db["transaction_type"] == "payment"
        assert payment_in_db["direction"] == "out"
        assert payment_in_db["description"] == f"Payment for order #{paid_order['id']}"
        assert payment_in_db["created_at"] is not None

    @allure.story("Confirmed order is paid and balance decreases")
    def test_created_transaction_payment_schema(self, paid_order: dict, db: DBManager) -> None:
        transaction_schema = db.get_transaction_by_id(paid_order["transaction_id"])
        assert isinstance(transaction_schema["id"], int)
        assert isinstance(transaction_schema["account_id"], int)
        assert isinstance(transaction_schema["amount"], float)
        assert isinstance(transaction_schema["transaction_type"], str)
        assert isinstance(transaction_schema["direction"], str)
        assert isinstance(transaction_schema["description"], str)

    @allure.story("Confirmed order is paid and balance decreases")
    def test_created_transaction_payment_balance_decreases_in_db(
        self, paid_order: dict, user_account: dict, created_transaction_deposit: dict, db: DBManager
    ) -> None:
        payment_in_db = db.get_transaction_by_id(paid_order["transaction_id"])
        balance_after = db.get_account_balance(user_account["id"])
        assert balance_after == created_transaction_deposit["amount"] - payment_in_db["amount"]
