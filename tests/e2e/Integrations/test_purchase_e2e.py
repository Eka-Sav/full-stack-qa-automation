"""E2E integration (API + DB): an order is created, confirmed and paid, the balance decreases, the payment is saved."""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints
from database.db_manager import DBManager

pytestmark = [allure.epic("Cart & Orders"), pytest.mark.integration]


@allure.feature("Checkout")
class TestE2EPurchase:
    @allure.story("User buys a product from cart to payment")
    @allure.title("Order created, confirmed and paid via API decreases balance and saves payment in DB")
    def test_e2e_purchase(
        self,
        api_client: APIClient,
        created_user: dict,
        created_product: dict,
        created_transaction_deposit: dict,
        user_account: dict,
        db: DBManager,
    ) -> None:
        with allure.step("Balance before purchase equals the deposit"):
            response_before = api_client.get(Endpoints.accounts_by_account_number(created_user["account_number"]))
            assert response_before.status_code == 200, f"Unexpected response: {response_before.text}"
            balance_before = response_before.json()["balance"]
            assert balance_before == created_transaction_deposit["amount"]

        with allure.step("Create an order"):
            order_data = {
                "user_id": created_user["id"],
                "product_id": created_product["id"],
                "quantity": 1,
            }
            order_response = api_client.post(Endpoints.ORDERS, json=order_data)
            assert order_response.status_code == 201, f"Unexpected response: {order_response.text}"
            created_order = order_response.json()
            assert created_order["status"] == "pending"

        with allure.step("Confirm the order"):
            confirm_response = api_client.patch(Endpoints.order_confirm(created_order["id"]))
            assert confirm_response.status_code == 200, f"Unexpected response: {confirm_response.text}"
            confirmed_order = confirm_response.json()
            assert confirmed_order["status"] == "confirmed"

        with allure.step("Pay the order"):
            pay_response = api_client.post(Endpoints.order_pay(confirmed_order["id"]))
            assert pay_response.status_code == 200, f"Unexpected response: {pay_response.text}"
            paid_order = pay_response.json()
            assert paid_order["status"] == "paid", f"Expected status 'paid', got '{paid_order['status']}'"

        with allure.step("Balance decreases by the order total"):
            expected_total = created_product["price"] * order_data["quantity"]
            response_after = api_client.get(Endpoints.accounts_by_account_number(created_user["account_number"]))
            assert response_after.status_code == 200, f"Unexpected response: {response_after.text}"
            balance_after = response_after.json()["balance"]
            assert balance_after == pytest.approx(balance_before - expected_total, rel=1e-6), (
                f"Expected balance {balance_before - expected_total}, got {balance_after}"
            )

        with allure.step("Payment transaction is saved in DB"):
            transactions = db.get_transactions_by_account(user_account["id"])
            payment_transactions = [
                tx
                for tx in transactions
                if tx["transaction_type"] == "payment" and tx.get("order_id") == paid_order["id"]
            ]
            assert len(payment_transactions) == 1,f"Payment transaction count {len(payment_transactions)} != 1"
            payment_tx = payment_transactions[0]
            assert payment_tx["amount"] == pytest.approx(expected_total, rel=1e-6), (
                f"Payment transaction amount {payment_tx['amount']} does not match order total {expected_total}"
            )
