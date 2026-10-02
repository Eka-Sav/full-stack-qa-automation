"""DB checks for registration: user record and the account created with it."""

import allure
import pytest

from database.db_manager import DBManager

pytestmark = [allure.epic("Account Management"), pytest.mark.db]


@allure.feature("Registration")
class TestCreatedUserDB:
    @allure.story("User is registered with a linked account")
    def test_created_user_saved_in_db(self, created_user: dict, db: DBManager) -> None:
        user_in_db = db.get_user_by_id(created_user["id"])
        assert user_in_db is not None
        assert user_in_db["username"] == created_user["username"]
        assert user_in_db["id"] == created_user["id"]
        assert user_in_db["email"] == created_user["email"]

    @allure.story("User is registered with a linked account")
    def test_created_user_schema_in_db(self, created_user: dict, db: DBManager) -> None:
        user_schema_in_db = db.get_user_by_id(created_user["id"])
        assert isinstance(user_schema_in_db["id"], int)
        assert isinstance(user_schema_in_db["username"], str)
        assert isinstance(user_schema_in_db["email"], str)
        assert isinstance(user_schema_in_db["hashed_password"], str)
        assert user_schema_in_db["created_at"] is not None


@allure.feature("Registration")
class TestAccountUserDB:
    @allure.story("User is registered with a linked account")
    def test_account_user_saved_in_db(self, created_user: dict, db: DBManager) -> None:
        account_in_db = db.get_account_by_user_id(created_user["id"])
        assert account_in_db is not None
        assert account_in_db["user_id"] == created_user["id"]
        assert account_in_db["balance"] == 0.0
        assert account_in_db["account_number"] is not None
        assert account_in_db["currency"] == "USD"
        assert account_in_db["created_at"] is not None

    @allure.story("User is registered with a linked account")
    def test_account_user_schema_in_db(self, created_user: dict, db: DBManager) -> None:
        account_in_db = db.get_account_by_user_id(created_user["id"])
        assert isinstance(account_in_db["id"], int)
        assert isinstance(account_in_db["user_id"], int)
        assert isinstance(account_in_db["account_number"], str)
        assert isinstance(account_in_db["balance"], float)
        assert isinstance(account_in_db["currency"], str)
