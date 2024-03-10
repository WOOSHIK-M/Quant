import json
import time
import uuid
from typing import Any

import jwt
import requests

from api_urls import UPBIT_OPEN_API_MARKET_URL


def get_account_info(url: str, access_key: str, secret_key: str) -> tuple[bool, dict]:
    """Get account information."""
    payload = {"access_key": access_key, "nonce": str(uuid.uuid4())}
    token = jwt.encode(payload=payload, key=secret_key)
    return request_info(url=url, headers={"Authorization": f"Bearer {token}"})


def request_info(
    url: str, headers: str = None, params: str = None, is_order_request: bool = False
) -> Any:
    """Get data from the given url.

    Reference:
        https://docs.upbit.com/docs/user-request-guide
    """
    time.sleep(1 / 8)
    res = requests.get(url=url, headers=headers, params=params)

    # check if the response is normal
    if res.status_code in [400, 401]:
        return False, None
    if res.text is None:
        return False, None
    return True, json.loads(res.text)


def get_all_markets() -> list[dict[str, str]]:
    """Get all markets supported by Upbit.

    Note:
        - It returns the list of market info.
        - market info contains (market code, korean name, english name) of each.
    """
    _, markets = request_info(url=UPBIT_OPEN_API_MARKET_URL + "/all")
    return markets
