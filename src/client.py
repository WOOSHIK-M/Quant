import datetime
import json
import time
import uuid
from abc import ABCMeta
from typing import Any

import jwt
import pandas as pd
import requests

from id import PersonalKeys
from src.structure import Market

UPBIT_OPEN_API_SERVER_URI = "https://api.upbit.com/v1"


# Example (id.py) :
#
# from dataclasses import dataclass
#
# @dataclass
# class PersonalKeys:
#     access_key: str = ""
#     secret_key: str = ""
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
        res = requests.get(url=url, headers=headers, params=params)

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


class UpbitClient(UrlClient):
    """Do backtesting."""

    # https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C
    MARKET_URL = UPBIT_OPEN_API_SERVER_URI + "/market"
    # https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1
    OHLCV_URL = UPBIT_OPEN_API_SERVER_URI + "/candles"

    def __init__(self) -> None:
        """Initialize."""
        self.markets = self._get_markets()

    def _get_markets(self) -> dict[str, Market]:
        """Get all available market codes.

        Returns:
            {market_code: Market_dataclass}
        """
        url = self.MARKET_URL + "/all"

        markets = self._get(url=url)
        return {market["market"]: Market(**market) for market in markets}

    def get_candles(
        self,
        unit: str = "days",
        market_code: str = "KRW-BTC",
        sub_unit: int = 60,
    ) -> pd.DataFrame:
        """Get candles.

        It always requests all candle data of the given market code.
        """
        assert unit in ["minutes", "days", "weeks"], f"Unknown unit [{unit}]"
        assert market_code in self.markets, f"Unknown market code {market_code}"

        # make url
        url = self.OHLCV_URL + f"/{unit}"
        if unit == "minutes":
            url += f"/{sub_unit}"

        # calculate count interval
        interval = 60
        if unit == "minutes":
            interval *= sub_unit
        elif unit == "days":
            interval *= 60 * 24
        elif unit == "weeks":
            interval *= 60 * 24 * 7

        # get all candle data
        to_date = datetime.datetime.today()

        data = []
        headers = {"accept": "application/json"}
        params = {"market": market_code, "count": 200}
        while True:
            params["to"] = to_date.strftime("%Y-%m-%d %H:%M:%S")
            candles = self._get(url=url, headers=headers, params=params)

            if not candles:
                break

            data += candles
            print(len(data), to_date)
            to_date = to_date - datetime.timedelta(seconds=params["count"] * interval)

            # api only allow 30 times for each second
            time.sleep(0.05)
        return pd.DataFrame.from_dict(data)
