import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# test-side DB access, intentionally independent from the backend package
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set, check .dockerignore")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class DBManager:
    """Direct database access for test assertions."""

    def __init__(self):
        self.session: Session = SessionLocal()

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # users

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        result = self.session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id}).fetchone()
        return dict(result._mapping) if result else None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        result = self.session.execute(
            text("SELECT * FROM users WHERE username = :username"), {"username": username}
        ).fetchone()
        return dict(result._mapping) if result else None

    def count_users(self) -> int:
        return self.session.execute(text("SELECT COUNT(*) FROM users")).scalar()

    def delete_user_by_username(self, username: str) -> None:
        self.session.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})
        self.session.commit()

    def delete_user_by_email(self, email: str) -> None:
        self.session.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
        self.session.commit()

    # accounts

    def get_account_by_user_id(self, user_id: int) -> Optional[dict]:
        result = self.session.execute(text("SELECT * FROM accounts WHERE user_id = :uid"), {"uid": user_id}).fetchone()
        return dict(result._mapping) if result else None

    def get_account_balance(self, account_id: int) -> Optional[float]:
        result = self.session.execute(
            text("SELECT balance FROM accounts WHERE id = :id"), {"id": account_id}
        ).fetchone()
        return result[0] if result else None

    # transactions

    def get_transaction_by_id(self, tx_id: int) -> Optional[dict]:
        result = self.session.execute(text("SELECT * FROM transactions WHERE id = :id"), {"id": tx_id}).fetchone()
        return dict(result._mapping) if result else None

    def count_transactions_for_account(self, account_id: int) -> int:
        return self.session.execute(
            text("SELECT COUNT(*) FROM transactions WHERE account_id = :id"), {"id": account_id}
        ).scalar()

    def get_transactions_by_account(self, account_id: int) -> list:
        results = self.session.execute(
            text("SELECT * FROM transactions WHERE account_id = :id ORDER BY created_at DESC"), {"id": account_id}
        ).fetchall()
        return [dict(r._mapping) for r in results]

    def get_total_received(self, account_id: int) -> float:
        result = self.session.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE account_id = :id AND direction = 'in'"),
            {"id": account_id},
        ).scalar()
        return result

    def get_total_spent(self, account_id: int) -> float:
        result = self.session.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE account_id = :id AND direction = 'out'"),
            {"id": account_id},
        ).scalar()
        return result

    # products

    def get_product_by_id(self, product_id: int) -> Optional[dict]:
        result = self.session.execute(text("SELECT * FROM products WHERE id = :id"), {"id": product_id}).fetchone()
        return dict(result._mapping) if result else None

    def count_active_products(self) -> int:
        return self.session.execute(text("SELECT COUNT(*) FROM products WHERE is_active = true")).scalar()

    # orders

    def get_order_by_id(self, order_id: int) -> Optional[dict]:
        result = self.session.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}).fetchone()
        return dict(result._mapping) if result else None

    def get_latest_order_by_user_id(self, user_id: int) -> Optional[dict]:
        result = self.session.execute(
            text("SELECT * FROM orders WHERE user_id = :uid ORDER BY id DESC LIMIT 1"),
            {"uid": user_id},
        ).fetchone()
        return dict(result._mapping) if result else None

    def count_orders_for_user(self, user_id: int) -> int:
        return self.session.execute(text("SELECT COUNT(*) FROM orders WHERE user_id = :id"), {"id": user_id}).scalar()
