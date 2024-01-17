import json
import uuid

import jwt
import requests


def get_account_info(url: str, access_key: str, secret_key: str) -> tuple[bool, dict]:
    """Get account information."""
    payload = {"access_key": access_key, "nonce": str(uuid.uuid4())}
    token = jwt.encode(payload=payload, key=secret_key)

    response = requests.get(
        url=url,
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code in [400, 401]:
        return False, {}
    if response.text is None:
        return False, {}
    return True, json.loads(response.text)
