import json
import uuid
from abc import ABCMeta
from typing import Any

import jwt
import requests

UPBIT_OPEN_API_SERVER_URI = "https://api.upbit.com/v1"


class UrlClient(metaclass=ABCMeta):
    """Open api handler.

    Reference:
        https://docs.upbit.com/docs/create-authorization-request
    """

    def __init__(self, access_key: str, secret_key: str) -> None:
        """Initialize."""
        self.access_key = access_key
        self.secret_key = secret_key

    def _get_token(self) -> str:
        """Get jwt token."""
        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
        }
        return jwt.encode(payload=payload, key=self.secret_key)

    def _get(self, url: str, headers: str = None, params: str = None) -> Any:
        """Get data from the given url."""
        res = requests.get(url=url, headers=headers, params=params)

        # check if the response is normal
        if res.status_code in [400, 401]:
            raise NotImplementedError(f"Error Code: {res.status_code}")
        if res.text is None:
            raise NotImplementedError("Empty responese...")
        return json.loads(res.text)


class UpbitAccount(UrlClient):
    """Upbit account."""

    URL = UPBIT_OPEN_API_SERVER_URI + "/accounts"

    def __init__(self, access_key: str, secret_key: str) -> None:
        """Initialize."""
        super().__init__(access_key=access_key, secret_key=secret_key)

        self.account_info = self._get_account_info()

    def _get_account_info(self) -> list[dict[str, str]]:
        """Get the current account information."""
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        info = self._get(self.URL, headers=headers)
        return info

    def get_info(self, n_info: int = 10000) -> str:
        """Get account information."""
        msg = ""
        for info in self.account_info[:n_info]:
            msg += "\n".join([f"{key:<30}: {value}" for key, value in info.items()])
            msg += "\n" * 2

        if len(self.account_info) > n_info:
            msg += "and more ..."
        return msg
