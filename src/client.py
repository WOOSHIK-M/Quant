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

    def get_minute_candles(
        self,
        market_code: str = "KRW-BTC",
        unit: int = 240,
        count: int = 200,
    ) -> pd.DataFrame:
        """."""
        assert market_code in self.markets, "Unknown market code..."
        assert unit in [1, 3, 5, 15, 10, 30, 60, 240]

        url = self.OHLCV_URL + f"/minutes/{unit}"

        headers = {"accept": "application/json"}
        params = {"market": market_code}

        from_date = datetime.datetime.strptime("1995-03-05", "%Y-%m-%d")
        to_date = datetime.datetime.today()

        data = []
        while to_date > from_date:
            params = {
                "market": market_code,
                "to": to_date.strftime("%Y-%m-%d %H:%M:%S"),
                "count": min(count, (to_date - from_date).seconds * 60 * unit),
            }
            candles = self._get(url=url, headers=headers, params=params)

            if not candles:
                break

            data += candles
            to_date = max(from_date, to_date - datetime.timedelta(seconds=count * 60 * unit))

            # api only allow 30 times for each second
            time.sleep(0.05)
        return pd.DataFrame.from_dict(data)

    def get_day_candles(
        self,
        market_code: str = "KRW-BTC",
        count: int = 200,
    ) -> pd.DataFrame:
        """Get candles on a daily basis.

        Arguments:
            market: Market code.
            to: The last candle time(exclusive).
                Get the recent history if it is None.
                It has ISO8061 format(yyyy-MM-dd`T`HH:mm:ss`Z` or yyyy-MM-dd).
            count: The number of candles.
        """
        assert market_code in self.markets, "Unknown market code..."

        url = self.OHLCV_URL + "/days"

        headers = {"accept": "application/json"}
        params = {"market": market_code}

        from_date = datetime.datetime.strptime("1995-03-05", "%Y-%m-%d")
        to_date = datetime.datetime.today()

        data = []
        while to_date > from_date:
            params = {
                "market": market_code,
                "to": to_date.strftime("%Y-%m-%d %H:%M:%S"),
                "count": min(count, (to_date - from_date).days),
            }
            candles = self._get(url=url, headers=headers, params=params)

            if not candles:
                break

            data += candles
            to_date = max(from_date, to_date - datetime.timedelta(days=count))

            # api only allow 30 times for each second
            time.sleep(0.04)
        return pd.DataFrame.from_dict(data)
