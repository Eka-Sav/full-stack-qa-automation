import logging
import re
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from config.config import config
from pages.cart_page import CartPage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from pages.orders_page import OrdersPage
from pages.products_page import ProductsPage
from pages.transactions_page import TransactionsPage

logger = logging.getLogger(__name__)


# users and accounts


@pytest.fixture
def login_page(page) -> LoginPage:
    page.goto(config.FRONTEND_URL)
    return LoginPage(page)

@pytest.fixture
def registered_user_via_ui(login_page, user_data) -> dict:
    login_page.register(user_data["username"], user_data["email"], user_data["password"])
    return user_data

@pytest.fixture
def logged_in_page(login_page, created_user) -> Page:
    login_page.login(created_user["username"], created_user["password"])
    login_page.page.wait_for_url(re.compile("dashboard"))
    return login_page.page

@pytest.fixture
def logged_in_page_recipient(browser, created_recipient) -> Generator[Page, None, None]:
    context = browser.new_context()
    page = context.new_page()
    page.goto(config.FRONTEND_URL)
    second_login_page = LoginPage(page)
    second_login_page.login(created_recipient["username"], created_recipient["password"])
    page.wait_for_url(re.compile("dashboard"))
    yield page
    context.close()


# products

@pytest.fixture
def products_page(logged_in_page) -> ProductsPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/products")
    return ProductsPage(logged_in_page)


# cart

@pytest.fixture
def cart_page_empty(logged_in_page) -> CartPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/cart")
    return CartPage(logged_in_page)

@pytest.fixture
def cart_page(created_product, products_page) -> CartPage:
    products_page.add_product_confirm("1")
    products_page.navigate(f"{config.FRONTEND_URL}/cart")
    return CartPage(products_page.page)

@pytest.fixture
def cart_page_via_api(created_order, logged_in_page) -> CartPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/cart")
    return CartPage(logged_in_page)

# orders

@pytest.fixture
def orders_page(logged_in_page) -> OrdersPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/orders")
    return OrdersPage(logged_in_page)


# transactions

@pytest.fixture
def transactions_page(logged_in_page) -> TransactionsPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/transactions")
    return TransactionsPage(logged_in_page)

@pytest.fixture
def transactions_page_with_deposit(transactions_page) -> TransactionsPage:
    transactions_page.confirm_send_deposit("100", "deposit 1")
    return transactions_page

@pytest.fixture
def transactions_page_recipient(logged_in_page_recipient) -> TransactionsPage:
    logged_in_page_recipient.goto(f"{config.FRONTEND_URL}/transactions")
    return TransactionsPage(logged_in_page_recipient)


# dashboard

@pytest.fixture
def dashboard_page(logged_in_page) -> DashboardPage:
    return DashboardPage(logged_in_page)

@pytest.fixture
def dashboard_page_recipient(logged_in_page_recipient) -> DashboardPage:
    return DashboardPage(logged_in_page_recipient)

@pytest.fixture
def dashboard_page_sender(logged_in_page) -> DashboardPage:
    logged_in_page.goto(f"{config.FRONTEND_URL}/dashboard")
    return DashboardPage(logged_in_page)


# allure screenshots

TEST_RESULTS_DIR = Path("test-results")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item, nextitem):
    yield
    try:
        if TEST_RESULTS_DIR.is_dir():
            found = list(TEST_RESULTS_DIR.rglob("test-failed-*.png"))
            for file in found:
                allure.attach.file(
                    str(file),
                    name=file.name,
                    attachment_type=allure.attachment_type.PNG,
                )
                # remove after attaching so the next test does not pick it up
                file.unlink()
    except Exception as e:
        logger.warning(f"Error attaching screenshot: {e}")
