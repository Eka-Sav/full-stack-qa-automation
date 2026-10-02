"""UI tests for registration, login and logout on the login page."""

import re
import uuid

import allure
import pytest
from faker import Faker
from playwright.sync_api import expect

from config.config import config
from pages.login_page import LoginPage

pytestmark = [allure.epic("Account Management"), pytest.mark.ui]


@allure.feature("Registration")
class TestRegisterUser:
    @allure.story("User is registered with a linked account")
    @allure.title("Register with valid data")
    def test_successful_register(self, login_page: LoginPage, user_data: dict) -> None:
        login_page.register(user_data["username"], user_data["email"], user_data["password"])
        expect(login_page.success_message).to_be_visible()
        expect(login_page.switch_login).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: duplicate username or email")
    @allure.title("Register with an existing username")
    def test_duplicate_username_register(self, login_page: LoginPage, user_data: dict, faker: Faker) -> None:
        username = user_data["username"]
        login_page.register(username, user_data["email"], user_data["password"])
        login_page.register(username, faker.email(), faker.password())
        expect(login_page.error_message).to_have_text("Username already exists")
        expect(login_page.switch_login).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: duplicate username or email")
    @allure.title("Register with an existing email")
    def test_duplicate_email_register(self, login_page: LoginPage, user_data: dict, faker: Faker) -> None:
        email = user_data["email"]
        login_page.register(user_data["username"], user_data["email"], user_data["password"])
        login_page.register(f"user_{uuid.uuid4().hex[:8]}", email, faker.password())
        expect(login_page.error_message).to_have_text("Email already exists")
        expect(login_page.switch_login).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with an empty username")
    def test_empty_username_register(self, login_page: LoginPage, faker: Faker) -> None:
        login_page.register("", faker.email(), faker.password())
        expect(login_page.error_message).to_have_text("All fields are required")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with an empty email")
    def test_empty_email_register(self, login_page: LoginPage, faker: Faker) -> None:
        login_page.register(faker.user_name(), "", faker.password())
        expect(login_page.error_message).to_have_text("All fields are required")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with an empty password")
    def test_empty_password_register(self, login_page: LoginPage, faker: Faker) -> None:
        login_page.register(faker.user_name(), faker.email(), "")
        expect(login_page.error_message).to_have_text("All fields are required")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with all fields empty")
    def test_empty_fields_register(self, login_page: LoginPage) -> None:
        login_page.register("", "", "")
        expect(login_page.error_message).to_have_text("All fields are required")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with an email without @")
    def test_email_without_at_register(self, login_page: LoginPage, faker: Faker, user_data: dict) -> None:
        login_page.register(user_data["username"], "fakeemail.tt", faker.password())
        expect(login_page.error_message).to_have_text("Invalid email format")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with an email without a domain zone")
    def test_email_without_domain_register(self, login_page: LoginPage, faker: Faker, user_data: dict) -> None:
        login_page.register(user_data["username"], "fake@emailtt", faker.password())
        expect(login_page.error_message).to_have_text("Invalid email format")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with a username shorter than 3 characters")
    def test_min_username_register(self, login_page: LoginPage, faker: Faker) -> None:
        login_page.register("12", faker.email(), faker.password())
        expect(login_page.error_message).to_have_text("Username must be at least 3 characters")
        expect(login_page.register_button).to_be_visible()

    @pytest.mark.negative
    @allure.story("Registration rejected: invalid input")
    @allure.title("Register with a password shorter than 6 characters")
    def test_min_password_register(self, login_page: LoginPage, faker: Faker) -> None:
        login_page.register(faker.user_name(), faker.email(), "12345")
        expect(login_page.error_message).to_have_text("Password must be at least 6 characters")
        expect(login_page.register_button).to_be_visible()


@allure.feature("Authentication")
class TestLogin:
    @allure.story("User logs in")
    @allure.title("Log in with valid credentials")
    def test_successful_login(self, login_page: LoginPage, created_user: dict) -> None:
        login_page.login(created_user["username"], created_user["password"])
        expect(login_page.page).to_have_url(f"{config.FRONTEND_URL}/dashboard")

    @pytest.mark.negative
    @allure.story("Login rejected: invalid or missing credentials")
    @allure.title("Log in with a nonexistent username")
    def test_nonexistent_user_login(self, login_page: LoginPage, created_user: dict, faker: Faker) -> None:
        login_page.login(faker.user_name(), created_user["password"])
        expect(login_page.page).not_to_have_url(re.compile("dashboard"))
        expect(login_page.error_message).to_have_text("Invalid username or password")

    @pytest.mark.negative
    @allure.story("Login rejected: invalid or missing credentials")
    @allure.title("Log in with a wrong password")
    def test_wrong_password_login(self, login_page: LoginPage, created_user: dict, faker: Faker) -> None:
        login_page.login(created_user["username"], faker.password())
        expect(login_page.page).not_to_have_url(re.compile("dashboard"))
        expect(login_page.error_message).to_have_text("Invalid username or password")

    @pytest.mark.negative
    @allure.story("Login rejected: invalid or missing credentials")
    @allure.title("Log in with an empty username")
    def test_empty_user_login(self, login_page: LoginPage, created_user: dict) -> None:
        login_page.login("", created_user["password"])
        expect(login_page.page).not_to_have_url(re.compile("dashboard"))
        expect(login_page.error_message).to_have_text("Please fill in all fields")

    @pytest.mark.negative
    @allure.story("Login rejected: invalid or missing credentials")
    @allure.title("Log in with an empty password")
    def test_empty_password_login(self, login_page: LoginPage, created_user: dict) -> None:
        login_page.login(created_user["username"], "")
        expect(login_page.page).not_to_have_url(re.compile("dashboard"))
        expect(login_page.error_message).to_have_text("Please fill in all fields")


@allure.feature("Authentication")
class TestLogout:
    @allure.story("User logs out")
    @allure.title("Log out redirects to the login page")
    def test_successful_logout(self, login_page: LoginPage, created_user: dict) -> None:
        login_page.login(created_user["username"], created_user["password"])
        login_page.logout()
        expect(login_page.page).to_have_url(re.compile("login"))
