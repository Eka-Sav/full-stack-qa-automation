"""API tests for users: registration, login, account details"""

import allure
import pytest

from api.api_client import APIClient
from api.endpoints import Endpoints

pytestmark = [
    allure.epic("Account Management"),
    pytest.mark.api,
]


@allure.feature("Registration")
class TestCreateUsers:
    @allure.story("User is registered with a linked account")
    @pytest.mark.smoke
    def test_create_user_returns_201(self, api_client: APIClient, user_data: dict) -> None:
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 201, f"Unexpected response: {response.text}"
        new_user = response.json()
        assert new_user is not None
        assert new_user["id"] is not None
        assert new_user["username"] == user_data["username"]
        assert new_user["email"] == user_data["email"]
        assert "password" not in new_user

    @allure.story("User is registered with a linked account")
    def test_create_user_response_schema(self, created_user: dict) -> None:
        assert isinstance(created_user["id"], int)
        assert isinstance(created_user["username"], str)
        assert isinstance(created_user["email"], str)

    @allure.story("Registration rejected: duplicate username or email")
    @pytest.mark.negative
    def test_create_user_duplicate_username_returns_409(self, api_client: APIClient, created_user: dict) -> None:
        created_user["email"] = f"other_{created_user['email']}"
        response = api_client.post(Endpoints.USERS, json=created_user)
        assert response.status_code == 409, f"Unexpected response: {response.text}"
        assert "Username already exists" in response.json()["detail"]

    @allure.story("Registration rejected: duplicate username or email")
    @pytest.mark.negative
    def test_create_user_duplicate_email_returns_409(self, api_client: APIClient, created_user: dict) -> None:
        created_user["username"] = f"other_{created_user['username']}"
        response = api_client.post(Endpoints.USERS, json=created_user)
        assert response.status_code == 409, f"Unexpected response: {response.text}"
        assert "Email already exists" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_short_username_returns_400(self, api_client: APIClient, user_data: dict) -> None:
        user_data["username"] = "Ar"
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Username must be at least 3 characters" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("email", "notanemail"), ("email", "a@@b.com"), ("email", "a@b")])
    def test_create_user_invalid_format_email_returns_400(
        self, api_client: APIClient, user_data: dict, field: str, value: str
    ) -> None:
        user_data[field] = value
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Invalid email format" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [("password", "123"), ("password", "ab"), ("password", "12345")])
    def test_create_user_short_password_returns_400(
        self, api_client: APIClient, user_data: dict, field: str, value: str
    ) -> None:
        user_data[field] = value
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Password must be at least 6 characters" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_empty_username_returns_400(self, api_client: APIClient, user_data: dict) -> None:
        user_data["username"] = ""
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Username must be at least 3 characters" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_empty_email_returns_400(self, api_client: APIClient, user_data: dict) -> None:
        user_data["email"] = ""
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Invalid email format" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_empty_password_returns_400(self, api_client: APIClient, user_data: dict) -> None:
        user_data["password"] = ""
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 400, f"Unexpected response: {response.text}"
        assert "Password must be at least 6 characters" in response.json()["detail"]

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_invalid_type_username_returns_422(self, api_client: APIClient, user_data: dict) -> None:
        user_data["username"] = 12345345
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_invalid_type_password_returns_422(self, api_client: APIClient, user_data: dict) -> None:
        user_data["password"] = 12345345
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_missing_email_returns_422(self, api_client: APIClient, user_data: dict) -> None:
        user_data.pop("email")
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_missing_username_returns_422(self, api_client: APIClient, user_data: dict) -> None:
        user_data.pop("username")
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Registration rejected: invalid input")
    @pytest.mark.negative
    def test_create_user_missing_password_returns_422(self, api_client: APIClient, user_data: dict) -> None:
        user_data.pop("password")
        response = api_client.post(Endpoints.USERS, json=user_data)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Authentication")
class TestLogin:
    @allure.story("User logs in")
    @pytest.mark.smoke
    def test_login_returns_200(self, api_client: APIClient, created_user: dict) -> None:
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        user_id = response.json()["user_id"]
        assert response.json()["access_token"] is not None
        assert response.json()["token_type"] == "bearer"
        assert isinstance(user_id, int)
        assert user_id is not None

    @allure.story("User logs in")
    def test_login_user_response_schema(self, api_client: APIClient, created_user: dict) -> None:
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        data = response.json()
        assert isinstance(data["access_token"], str)
        assert isinstance(data["token_type"], str)
        assert isinstance(data["user_id"], int)

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_nonexistent_username_returns_401(self, api_client: APIClient) -> None:
        response = api_client.post(
            Endpoints.LOGIN,
            json={
                "username": "ghost_user_xyz",
                "password": "somepassword",
            },
        )
        assert response.status_code == 401, f"Unexpected response: {response.text}"

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_empty_username_returns_401(self, api_client: APIClient, created_user: dict) -> None:
        created_user["username"] = ""
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 401, f"Unexpected response: {response.text}"
        assert "Invalid username or password" in response.json()["detail"]

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_empty_password_returns_401(self, api_client: APIClient, created_user: dict) -> None:
        created_user["password"] = ""
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 401, f"Unexpected response: {response.text}"
        assert "Invalid username or password" in response.json()["detail"]

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_invalid_value_username_returns_401(self, api_client: APIClient, created_user: dict) -> None:
        created_user["username"] = "wrongname"
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 401, f"Unexpected response: {response.text}"
        assert "Invalid username or password" in response.json()["detail"]

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_invalid_value_password_returns_401(self, api_client: APIClient, created_user: dict) -> None:
        created_user["password"] = "wrongpassword"
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 401, f"Unexpected response: {response.text}"
        assert "Invalid username or password" in response.json()["detail"]

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_missing_username_returns_422(self, api_client: APIClient, created_user: dict) -> None:
        created_user.pop("username")
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 422, f"Unexpected response: {response.text}"

    @allure.story("Login rejected: invalid or missing credentials")
    @pytest.mark.negative
    def test_login_missing_password_returns_422(self, api_client: APIClient, created_user: dict) -> None:
        created_user.pop("password")
        response = api_client.post(Endpoints.LOGIN, json=created_user)
        assert response.status_code == 422, f"Unexpected response: {response.text}"


@allure.feature("Account Details")
class TestAccount:
    @allure.story("Account details are retrievable")
    @pytest.mark.smoke
    def test_account_returns_200(self, api_client: APIClient, created_user: dict) -> None:
        response = api_client.get(Endpoints.accounts(created_user["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        account = response.json()[0]
        assert account["id"] is not None
        assert account["account_number"] is not None
        assert account["balance"] is not None
        assert account["currency"] is not None

    @allure.story("Account details are retrievable")
    def test_account_user_response_schema(self, api_client: APIClient, created_user: dict) -> None:
        response = api_client.get(Endpoints.accounts(created_user["id"]))
        assert response.status_code == 200, f"Unexpected response: {response.text}"
        data = response.json()[0]
        assert isinstance(data["id"], int)
        assert isinstance(data["account_number"], str)
        assert isinstance(data["balance"], float)
        assert isinstance(data["currency"], str)

    @allure.story("Account lookup rejected: user not found or invalid")
    @pytest.mark.negative
    def test_account_nonexistent_user_id_returns_404(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.accounts(12312313))
        assert response.status_code == 404, f"Unexpected response: {response.text}"
        assert "User not found" in response.json()["detail"]["error_message"]

    @allure.story("Account lookup rejected: user not found or invalid")
    @pytest.mark.negative
    def test_account_invalid_type_user_id_returns_422(self, api_client: APIClient) -> None:
        response = api_client.get(Endpoints.accounts("qwerty"))
        assert response.status_code == 422, f"Unexpected response: {response.text}"
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in response.json()["detail"][0]["msg"]
        )
