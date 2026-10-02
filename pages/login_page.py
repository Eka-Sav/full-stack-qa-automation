from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.switch_register = page.get_by_test_id("switch-register")
        self.register_button = page.get_by_test_id("register-button")
        self.switch_login = page.get_by_test_id("switch-login")
        self.login_button = page.get_by_test_id("login-button")
        self.username_input = page.get_by_test_id("username-input")
        self.email_input = page.get_by_test_id("email-input")
        self.password_input = page.get_by_test_id("password-input")
        self.toggle_password = page.get_by_test_id("toggle-password")
        self.error_message = page.get_by_test_id("error-message")
        self.success_message = page.get_by_test_id("success-message")

    def register(self, username: str, email: str, password: str) -> None:
        self.switch_register.click()
        self.username_input.fill(username)
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.register_button.click()

    def login(self, username: str, password: str) -> None:
        self.switch_login.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
