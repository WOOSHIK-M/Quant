import json
import time
import uuid
from abc import ABCMeta
from datetime import datetime, timedelta
from typing import Any

import jwt
import pandas as pd
import requests

try:
    from api_keys import PersonalKeys

    mykeys = PersonalKeys()
except Exception:
    print("Please make a id.py first.")

from src.structure import ChartProperty, Market

UPBIT_OPEN_API_SERVER_URI = "https://api.upbit.com/v1"


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
    """Do backtesting.

    References:
        https://docs.upbit.com/reference
    """

    MARKET_URL = UPBIT_OPEN_API_SERVER_URI + "/market"
    OHLCV_URL = UPBIT_OPEN_API_SERVER_URI + "/candles"

    UNIT_OPTIONS = ["minutes", "days", "weeks"]
    SUB_UNIT_OPTIONS = [1, 3, 5, 15, 10, 30, 60, 240]

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

    def get_candlesticks(self, chart_property: ChartProperty = None) -> pd.DataFrame:
        """Get candles.

        It always requests all candle data of the given market code.
        """
        chart_property = chart_property or ChartProperty()

        market_code = chart_property.market_code
        unit = chart_property.unit
        sub_unit = chart_property.sub_unit
        fname = chart_property.fname

        # check validation
        assert market_code in self.markets, f"Unknown market code [{market_code}]"
        assert unit in self.UNIT_OPTIONS, f"Unknown unit [{unit}]"
        assert sub_unit in self.SUB_UNIT_OPTIONS, f"Unknown sub_unit [{sub_unit}]"

        # load previous data if it exists
        data, from_when = pd.DataFrame(), datetime.min
        if fname.is_file():
            data = pd.read_pickle(fname)
            from_when = pd.to_datetime(data["candle_date_time_kst"])[0]

        # request new data
        newest_data = self._request_candle_sticks(
            market_code=market_code,
            unit=unit,
            sub_unit=sub_unit,
            from_when=from_when,
        )
        data = pd.concat([newest_data, data], ignore_index=True, verify_integrity=True)

        # save the data
        data.to_pickle(fname)
        return data

    def _request_candle_sticks(
        self,
        market_code: str,
        unit: str,
        sub_unit: int,
        from_when: datetime,
    ) -> pd.DataFrame:
        """Request the candle stick data."""
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
        to_date = datetime.today()

        data = []
        headers = {"accept": "application/json"}
        params = {"market": market_code, "count": 200}
        while True:
            params["to"] = to_date.strftime("%Y-%m-%d %H:%M:%S")
            candles = self._get(url=url, headers=headers, params=params)
            data += candles

            if not candles or from_when >= datetime.fromisoformat(
                candles[-1]["candle_date_time_kst"]
            ):
                break

            # api only allow 30 times for each second
            time.sleep(0.05)
            to_date = to_date - timedelta(seconds=params["count"] * interval)

        data = pd.DataFrame.from_dict(data)
        return data[pd.to_datetime(data["candle_date_time_kst"]) > from_when]
