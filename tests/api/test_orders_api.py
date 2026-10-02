"""API tests for /orders: create, get, cancel, confirm, pay"""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints

pytestmark = [
    allure.epic("Cart & Orders"),
    pytest.mark.api,
]


@allure.feature("Order Creation")
class TestCreateOrder:
    @allure.story("Order is created")
    @pytest.mark.smoke
    def test_create_order_returns_201(self, api_client: APIClient, order_data: dict) -> None:
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        new_order = response.json()
        assert new_order is not None
        assert new_order["id"] is not None
        assert new_order["user_id"] == order_data["user_id"]
        assert new_order["product_id"] == order_data["product_id"]
        assert new_order["quantity"] == order_data["quantity"]
        assert new_order["total_price"] is not None
        assert new_order["status"] == "pending"
        assert new_order["created_at"] is not None

    @allure.story("Order is created")
    def test_created_order_response_schema(self, created_order: dict) -> None:
        assert isinstance(created_order["id"], int)
        assert isinstance(created_order["user_id"], int)
        assert isinstance(created_order["product_id"], int)
        assert isinstance(created_order["quantity"], int)
        assert isinstance(created_order["total_price"], float)
        assert isinstance(created_order["status"], str)

    @allure.story("Order creation rejected: user or product not found")
    @pytest.mark.negative
    def test_create_order_nonexistent_user_id_returns_404(self, api_client: APIClient, order_data: dict) -> None:
        order_data["user_id"] = 123123123
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "User not found" in response.json()["detail"]

    @allure.story("Order creation rejected: user or product not found")
    @pytest.mark.negative
    def test_create_order_nonexistent_product_id_returns_404(self, api_client: APIClient, order_data: dict) -> None:
        order_data["product_id"] = 12123123123
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Product not found" in response.json()["detail"]["error_message"]

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("user_id", 0), ("user_id", -1)])
    def test_create_order_invalid_value_user_id_returns_422(
        self, api_client: APIClient, order_data: dict, field: str, value: int
    ) -> None:
        order_data[field] = value
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert "Input should be greater than 0" in response.json()["detail"][0]["msg"]

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("product_id", 0), ("product_id", -1)])
    def test_create_order_invalid_value_product_id_returns_422(
        self, api_client: APIClient, order_data: dict, field: str, value: int
    ) -> None:
        order_data[field] = value
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert "Input should be greater than 0" in response.json()["detail"][0]["msg"]

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("quantity", 0), ("quantity", -1)])
    def test_create_order_invalid_value_quantity_returns_400(
        self, api_client: APIClient, order_data: dict, field: str, value: int
    ) -> None:
        order_data[field] = value
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Quantity must be positive" in response.json()["detail"]

    @allure.story("Order creation rejected: product not available")
    @pytest.mark.negative
    def test_create_order_product_not_available_returns_400(
        self, api_client: APIClient, order_data: dict, deactivated_product: dict
    ) -> None:
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Product is not available" in response.json()["detail"]

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_order_invalid_type_user_id_returns_422(self, api_client: APIClient, order_data: dict) -> None:
        order_data["user_id"] = ""
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_order_invalid_type_product_id_returns_422(self, api_client: APIClient, order_data: dict) -> None:
        order_data["product_id"] = ""
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_order_invalid_type_quantity_returns_422(self, api_client: APIClient, order_data: dict) -> None:
        order_data["quantity"] = ""
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_order_missing_user_id_returns_422(self, api_client: APIClient, order_data: dict) -> None:
        order_data.pop("user_id")
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Order creation rejected: invalid input")
    @pytest.mark.negative
    def test_create_order_missing_product_id_returns_422(self, api_client: APIClient, order_data: dict) -> None:
        order_data.pop("product_id")
        response = api_client.post(Endpoints.ORDERS, json=order_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Order History")
class TestGetOrdersListByUserId:
    @allure.story("User orders are listed and retrievable")
    @pytest.mark.smoke
    def test_get_orders_list_by_user_id_response_200(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.get(Endpoints.orders_by_user_id(created_order["user_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        users_orders_list = response.json()
        assert isinstance(users_orders_list, list)
        assert len(users_orders_list) > 0
        order_first = users_orders_list[0]
        assert order_first["id"] == created_order["id"]
        assert order_first["id"] is not None
        assert order_first["product_id"] is not None
        assert order_first["quantity"] is not None
        assert order_first["total_price"] is not None
        assert order_first["status"] == "pending"
        assert order_first["created_at"] is not None

    @allure.story("User orders are listed and retrievable")
    def test_get_orders_list_by_user_id_response_schema(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.get(Endpoints.orders_by_user_id(created_order["user_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        users_order_schema = response.json()[0]
        assert isinstance(users_order_schema["id"], int)
        assert isinstance(users_order_schema["product_id"], int)
        assert isinstance(users_order_schema["quantity"], int)
        assert isinstance(users_order_schema["total_price"], float)
        assert isinstance(users_order_schema["status"], str)
        assert users_order_schema["created_at"] is not None

    @allure.story("Order lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_orders_list_nonexistent_user_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.orders_by_user_id(99999999))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "User not found" in response.json()["detail"]

    @allure.story("Order lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_orders_list_invalid_type_user_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.orders_by_user_id("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Order History")
class TestGetOrder:
    @allure.story("User orders are listed and retrievable")
    @pytest.mark.smoke
    def test_get_order_returns_200(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.get(Endpoints.order(created_order["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_order = response.json()
        assert new_order is not None
        assert new_order["id"] == created_order["id"]
        assert new_order["user_id"] == created_order["user_id"]
        assert new_order["product_id"] == created_order["product_id"]
        assert new_order["quantity"] == created_order["quantity"]
        assert new_order["total_price"] == created_order["total_price"]
        assert new_order["status"] == "pending"
        assert new_order["created_at"] is not None

    @allure.story("User orders are listed and retrievable")
    def test_get_order_response_schema(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.get(Endpoints.order(created_order["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        order_schema = response.json()
        assert isinstance(order_schema["id"], int)
        assert isinstance(order_schema["product_id"], int)
        assert isinstance(order_schema["quantity"], int)
        assert isinstance(order_schema["total_price"], float)
        assert isinstance(order_schema["status"], str)
        assert order_schema["created_at"] is not None

    @allure.story("Order lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_order_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.order(99999999))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Order not found" in response.json()["detail"]["error_message"]

    @allure.story("Order lookup rejected: not found or invalid id")
    @pytest.mark.negative
    def test_get_order_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.order("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Order Cancellation")
class TestCancelOrder:
    @allure.story("Order is cancelled")
    @pytest.mark.smoke
    def test_cancel_order_returns_200(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.patch(Endpoints.order_cancel(created_order["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        canceled_order_status = response.json()
        assert canceled_order_status["status"] == "cancelled"

    @allure.story("Cancellation rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_cancel_order_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.patch(Endpoints.order_cancel(12312313))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Order not found" in response.json()["detail"]

    @allure.story("Cancellation rejected: invalid order state")
    @pytest.mark.negative
    def test_double_cancel_order_returns_400(self, api_client: APIClient, cancelled_order: dict) -> None:
        response = api_client.patch(Endpoints.order_cancel(cancelled_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Order is already cancelled" in response.json()["detail"]

    @allure.story("Cancellation rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_cancel_order_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.patch(Endpoints.order_cancel("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Order Confirmation")
class TestConfirmOrder:
    @allure.story("Pending order is confirmed")
    @pytest.mark.smoke
    def test_confirm_order_returns_200(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.patch(Endpoints.order_confirm(created_order["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        confirm_order_status = response.json()
        assert confirm_order_status["status"] == "confirmed"

    @allure.story("Confirmation rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_confirm_order_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.patch(Endpoints.order_confirm(12312313))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Order not found" in response.json()["detail"]["error_message"]

    @allure.story("Confirmation rejected: invalid order state")
    @pytest.mark.negative
    def test_double_confirm_order_returns_400(self, api_client: APIClient, confirmed_order: dict) -> None:
        response = api_client.patch(Endpoints.order_confirm(confirmed_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Order is already confirmed" in response.json()["detail"]

    @allure.story("Confirmation rejected: invalid order state")
    @pytest.mark.negative
    def test_confirm_canceled_order_returns_400(self, api_client: APIClient, cancelled_order: dict) -> None:
        response = api_client.patch(Endpoints.order_confirm(cancelled_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Cannot confirm a cancelled order" in response.json()["detail"]

    @allure.story("Confirmation rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_confirm_order_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.patch(Endpoints.order_confirm("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Order Payment")
class TestPayOrder:
    @allure.story("Confirmed order is paid and balance decreases")
    @pytest.mark.smoke
    def test_pay_order_returns_200(
        self,
        api_client: APIClient,
        confirmed_order: dict,
        created_transaction_deposit: dict,
    ) -> None:
        pay_response = api_client.post(Endpoints.order_pay(confirmed_order["id"]))
        assert pay_response.status_code == 200, f"Unexpected response: {pay_response.text}"
        paid_order_status = pay_response.json()
        assert paid_order_status["status"] == "paid"

    @allure.story("Payment rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_pay_order_nonexistent_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.post(Endpoints.order_pay(12312313))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "Order not found" in response.json()["detail"]

    @allure.story("Payment rejected: invalid order state")
    @pytest.mark.negative
    def test_double_pay_order_returns_400(self, api_client: APIClient, paid_order: dict) -> None:
        response = api_client.post(Endpoints.order_pay(paid_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Order is already paid" in response.json()["detail"]

    @allure.story("Payment rejected: invalid order state")
    @pytest.mark.negative
    def test_pay_canceled_order_returns_400(self, api_client: APIClient, cancelled_order: dict) -> None:
        response = api_client.post(Endpoints.order_pay(cancelled_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Cannot pay a cancelled order" in response.json()["detail"]

    @allure.story("Payment rejected: invalid order state")
    @pytest.mark.negative
    def test_pay_pending_order_returns_400(self, api_client: APIClient, created_order: dict) -> None:
        response = api_client.post(Endpoints.order_pay(created_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Order must be confirmed before payment" in response.json()["detail"]

    @allure.story("Payment rejected: insufficient funds")
    @pytest.mark.negative
    def test_pay_order_insufficient_funds_returns_400(self, confirmed_order: dict, api_client: APIClient) -> None:
        response = api_client.post(Endpoints.order_pay(confirmed_order["id"]))
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Insufficient funds" in response.json()["detail"]

    @allure.story("Payment rejected: order not found or invalid id")
    @pytest.mark.negative
    def test_pay_order_invalid_type_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.post(Endpoints.order_pay("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )


@allure.feature("Order Payment")
class TestGetPaymentsListByAccountId:
    @allure.story("Payment record is retrievable")
    def test_get_payment_list_by_account_id_response_200(
        self, api_client: APIClient, paid_order: dict, user_account: dict
    ) -> None:
        response = api_client.get(Endpoints.transaction_by_account(user_account["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        payments_list = response.json()
        assert isinstance(payments_list, list)
        assert len(payments_list) > 0
        payment_response = next((t for t in payments_list if t["id"] == paid_order["transaction_id"]), None)
        assert payment_response is not None
        assert payment_response["amount"] is not None
        assert payment_response["transaction_type"] == "payment"
        assert payment_response["description"] == f"Payment for order #{paid_order['id']}"
        assert payment_response["direction"] == "out"
        assert payment_response["created_at"] is not None


@allure.feature("Order Payment")
class TestGetPaymentById:
    @allure.story("Payment record is retrievable")
    def test_get_payment_by_id_returns_200(self, api_client: APIClient, paid_order: dict) -> None:
        response = api_client.get(Endpoints.transaction(paid_order["transaction_id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        new_payment = response.json()
        assert new_payment is not None
        assert new_payment["amount"] is not None
        assert new_payment["transaction_type"] == "payment"
        assert new_payment["description"] == f"Payment for order #{paid_order['id']}"
        assert new_payment["direction"] == "out"
        assert new_payment["created_at"] is not None
