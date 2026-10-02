"""E2E: a product bought via UI is paid from the cart and reflected on orders, transactions, dashboard and in the DB."""

import uuid
from typing import Callable

import allure
import pytest
from playwright.sync_api import expect

from config.config import config
from database.db_manager import DBManager
from pages.cart_page import CartPage
from pages.dashboard_page import DashboardPage
from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage
from pages.transactions_page import TransactionsPage

pytestmark = [allure.epic("Cart & Orders"), pytest.mark.e2e, pytest.mark.ai_generated]


@allure.feature("Checkout")
class TestE2EProductPurchaseUI:
    @allure.story("User buys a product from cart to payment")
    @allure.title("Product bought via UI is paid from cart and reflected on orders, transactions, dashboard and in DB")
    def test_e2e_buy_product(
        self,
        created_transaction_deposit: dict,
        created_user: dict,
        user_account: dict,
        products_page: ProductsPage,
        transactions_page: TransactionsPage,
        dashboard_page: DashboardPage,
        cart_page_empty: CartPage,
        orders_page: OrdersPage,
        product_factory: Callable[..., dict],
        db: DBManager,
    ) -> None:
        with allure.step("Before purchase: Transactions page balance matches DB"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            expect(transactions_page.balance_amount).not_to_have_text("$0.00")
            balance_transactions_before = transactions_page.get_balance()
            balance_before_db = db.get_account_balance(user_account["id"])
            assert balance_transactions_before == balance_before_db, (
                f"Transactions page balance {balance_transactions_before} != DB balance {balance_before_db} "
                f"before purchase"
            )

        with allure.step("Before purchase: Dashboard stats match DB"):
            dashboard_page.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expect(dashboard_page.balance_amount).not_to_have_text("$0.00")
            balance_dashboard_before = dashboard_page.get_balance()
            received_before = dashboard_page.get_total_received()
            spent_before = dashboard_page.get_total_spent()
            count_before = dashboard_page.get_transactions_count()

            received_before_db = db.get_total_received(user_account["id"])
            spent_before_db = db.get_total_spent(user_account["id"])

            assert balance_dashboard_before == balance_before_db, (
                f"Dashboard balance {balance_dashboard_before} != DB balance {balance_before_db} before purchase"
            )
            assert received_before == received_before_db, (
                f"Dashboard received {received_before} != DB received {received_before_db} before purchase"
            )
            assert spent_before == spent_before_db, (
                f"Dashboard spent {spent_before} != DB spent {spent_before_db} before purchase"
            )
            assert count_before == 1, f"Expected 1 transaction before purchase (deposit), got {count_before}"

        with allure.step("Add the product to the cart"):
            product = product_factory(
                name=f"Test product {uuid.uuid4().hex[:8]}",
                price=created_transaction_deposit["amount"] - 9000,
            )
            NAME = product["name"]
            PRODUCT_PRICE = product["price"]
            QUANTITY = 1
            PURCHASE_AMOUNT = PRODUCT_PRICE * QUANTITY
            products_page.page.goto(f"{config.FRONTEND_URL}/products")
            products_page.search_product(NAME)
            products_page.add_product_confirm(str(QUANTITY))
            expect(products_page.order_success_message).to_be_visible()

        with allure.step("Pay the order in the cart"):
            cart_page_empty.page.goto(f"{config.FRONTEND_URL}/cart")
            cart_page_empty.pay_order()
            expect(cart_page_empty.success_message).to_be_visible()

        with allure.step("After purchase: order is paid in DB"):
            order_db = db.get_latest_order_by_user_id(created_user["id"])
            assert order_db["status"] == "paid", f"DB order status expected 'paid', got '{order_db['status']}'"

        with allure.step("Order is shown as paid on the Orders page"):
            orders_page.page.goto(f"{config.FRONTEND_URL}/orders")
            item = orders_page.get_order_item_by_id(order_db["id"])
            expect(item.get_by_test_id("order-status")).to_contain_text("Paid")

        with allure.step("After purchase: payment transaction is saved in DB"):
            transactions_db = db.get_transactions_by_account(user_account["id"])
            payment_transactions = [t for t in transactions_db if t["transaction_type"] == "payment"]
            assert len(payment_transactions) >= 1, (
                f"Expected at least 1 payment transaction in DB, found {len(payment_transactions)}"
            )
            payment_tx = payment_transactions[0]
            assert payment_tx["amount"] == PURCHASE_AMOUNT, (
                f"Payment transaction amount expected {PURCHASE_AMOUNT}, got {payment_tx['amount']}"
            )

        with allure.step("After purchase: Transactions page balance matches DB"):
            transactions_page.page.goto(f"{config.FRONTEND_URL}/transactions")
            expected_balance = balance_transactions_before - PURCHASE_AMOUNT
            expect(transactions_page.balance_amount).to_have_text(f"${expected_balance:.2f}")
            balance_transactions_after = transactions_page.get_balance()
            balance_after_db = db.get_account_balance(user_account["id"])

            assert balance_transactions_after == balance_after_db, (
                f"Transactions page balance {balance_transactions_after} != DB balance {balance_after_db} "
                f"after purchase"
            )
            assert balance_after_db == balance_before_db - PURCHASE_AMOUNT, (
                f"DB balance after purchase: expected {balance_before_db - PURCHASE_AMOUNT}, got {balance_after_db}"
            )

        with allure.step("After purchase: Dashboard stats match DB"):
            dashboard_page.page.goto(f"{config.FRONTEND_URL}/dashboard")
            expected_balance = balance_transactions_before - PURCHASE_AMOUNT
            expect(dashboard_page.balance_amount).to_have_text(f"${expected_balance:.2f}")
            balance_dashboard_after = dashboard_page.get_balance()
            received_after = dashboard_page.get_total_received()
            spent_after = dashboard_page.get_total_spent()
            count_after = dashboard_page.get_transactions_count()

            received_after_db = db.get_total_received(user_account["id"])
            spent_after_db = db.get_total_spent(user_account["id"])

            assert balance_dashboard_after == balance_after_db, (
                f"Dashboard balance after {balance_dashboard_after} != DB balance {balance_after_db}"
            )
            assert balance_dashboard_after == balance_dashboard_before - PURCHASE_AMOUNT, (
                f"Dashboard balance should decrease by {PURCHASE_AMOUNT}: "
                f"{balance_dashboard_before} -> {balance_dashboard_after}"
            )

            assert received_after == received_after_db, (
                f"Dashboard received {received_after} != DB received {received_after_db} after purchase"
            )
            assert received_after_db == received_before_db, (
                f"Total received should not change after purchase: before={received_before_db}, "
                f"after={received_after_db}"
            )

            assert spent_after == spent_after_db, (
                f"Dashboard spent {spent_after} != DB spent {spent_after_db} after purchase"
            )
            assert spent_after_db == spent_before_db + PURCHASE_AMOUNT, (
                f"Total spent should increase by {PURCHASE_AMOUNT}: {spent_before_db} -> {spent_after_db}"
            )

            assert count_after == count_before + 1, (
                f"Transaction count should increase by 1: before={count_before}, after={count_after}"
            )

        with allure.step("Purchase appears in Dashboard transaction history"):
            last_transaction_amount = dashboard_page.get_latest_transaction_amount()
            assert last_transaction_amount == PURCHASE_AMOUNT, (
                f"Last transaction amount on dashboard expected {PURCHASE_AMOUNT}, got {last_transaction_amount}"
            )
