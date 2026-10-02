class Endpoints:
    # users
    USERS = "/users"
    LOGIN = "/login"

    # transfers
    TRANSFERS = "/transfers"

    # transactions
    TRANSACTIONS = "/transactions"

    # products
    PRODUCTS = "/products"

    # orders
    ORDERS = "/orders"

    # health
    HEALTH = "/health"

    @staticmethod
    def accounts(user_id: int) -> str:
        return f"/accounts/{user_id}"

    @staticmethod
    def accounts_by_account_number(account_number: str) -> str:
        return f"/accounts?account_number={account_number}"

    @staticmethod
    def transaction(transaction_id: int) -> str:
        return f"/transactions/{transaction_id}"

    @staticmethod
    def transaction_by_account(account_id: int) -> str:
        return f"/transactions?account_id={account_id}"

    @staticmethod
    def product(product_id: int) -> str:
        return f"/products/{product_id}"

    @staticmethod
    def order(order_id: int) -> str:
        return f"/orders/{order_id}"

    @staticmethod
    def orders_by_user_id(user_id: int) -> str:
        return f"/orders?user_id={user_id}"

    @staticmethod
    def order_cancel(order_id: int) -> str:
        return f"/orders/{order_id}/cancel"

    @staticmethod
    def order_confirm(order_id: int) -> str:
        return f"/orders/{order_id}/confirm"

    @staticmethod
    def order_pay(order_id: int) -> str:
        return f"/orders/{order_id}/pay"
