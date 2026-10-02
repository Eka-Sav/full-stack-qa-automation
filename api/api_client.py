import requests

from config.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """Thin wrapper over requests.Session: base URL, default timeout and request/response logging."""

    def __init__(self):
        self.base_url = config.BASE_URL
        self.session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        # without a timeout a hanging backend would block the whole test run
        kwargs.setdefault("timeout", config.API_TIMEOUT)
        logger.debug(f"{method} {endpoint} | params={kwargs.get('params')} body={kwargs.get('json')}")
        response = self.session.request(method, self.base_url + endpoint, **kwargs)
        logger.debug(f"-> {response.status_code}")
        return response

    def get(self, endpoint: str, params: dict | None = None, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, json=json, **kwargs)

    def patch(self, endpoint: str, json: dict | None = None, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()
