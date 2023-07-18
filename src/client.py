import json
import uuid
from abc import ABCMeta
from typing import Any

import jwt
import requests

from id import PersonalKeys

UPBIT_OPEN_API_SERVER_URI = "https://api.upbit.com/v1/"

mykeys = PersonalKeys()


class UrlClient(metaclass=ABCMeta):
    """Open api handler.

    Reference:
        https://docs.upbit.com/docs/create-authorization-request
    """

    def _get_token(self) -> str:
        """Get jwt token."""
        payload = {
            "access_key": mykeys.access_key,
            "nonce": str(uuid.uuid4()),
        }
        return jwt.encode(payload=payload, key=mykeys.secret_key)

    def _get(self, url: str, headers: str = None, params: str = None) -> Any:
        """Get data from the given url."""
        res = requests.get(url=url, headers=headers)

        # check if the response is normal
        if res.status_code in [400, 401]:
            raise NotImplementedError(f"Error Code: {res.status_code}")
        if res.text is None:
            raise NotImplementedError("Empty responese...")
        return json.loads(res.text)

    def _pretty_print(self, data: dict[str, str], title: str) -> None:
        """Pretty print out."""
        n_hash = len(title) + 4
        print("#" * n_hash + f"\n# {title} #\n" + "#" * n_hash)
        for key, value in data.items():
            print(f"{key:<30}: {value}")


class UpbitAccount(UrlClient):
    """Upbit account."""

    URL = UPBIT_OPEN_API_SERVER_URI + "/accounts"

    def __init__(self) -> None:
        """Initialize."""
        self.account = self._get_account_info()

    def _get_account_info(self) -> dict[str, str]:
        """Get the current account information."""
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        info = self._get(self.URL, headers=headers)[0]
        self._pretty_print(info, title="Account INFO")
        return info


UpbitAccount()
