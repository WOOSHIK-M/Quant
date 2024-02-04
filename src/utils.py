import json
import uuid
from typing import Any

import jwt
import requests

def get_account_info(url: str, access_key: str, secret_key: str) -> tuple[bool, dict]:
    """Get account information."""
    payload = {"access_key": access_key, "nonce": str(uuid.uuid4())}
    token = jwt.encode(payload=payload, key=secret_key)
    return request_info(url=url, headers={"Authorization": f"Bearer {token}"})


def request_info(url: str, headers: str = None, params: str = None) -> Any:
    """Get data from the given url."""
    res = requests.get(url=url, headers=headers, params=params)

    # check if the response is normal
    if res.status_code in [400, 401]:
        return False, None
    if res.text is None:
        return False, None
    return True, json.loads(res.text)
