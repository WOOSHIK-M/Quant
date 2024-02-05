import itertools
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import src.utils as utils

UPBIT_OPEN_API_MARKET_URL = "https://api.upbit.com/v1/market"
OHLCV_URL = "https://api.upbit.com/v1/candles"

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)


class UpbitDataLoader:
    """Request candles and dump them to local device."""

    CHUNK_SIZE = 10000

    @property
    def periods(self) -> list[str]:
        """Get all available candle periods."""
        return [
            "weeks",
            "days",
            "240 minutes",
            "60 minutes",
            "30 minutes",
            "10 minutes",
            "15 minutes",
            "5 minutes",
            "3 minutes",
            "1 minutes",
        ]

    @property
    def market_list(self) -> list[str]:
        """Get all available market list."""
        _, markets = utils.request_info(url=UPBIT_OPEN_API_MARKET_URL + "/all")
        markets = [market["market"] for market in markets]
        return markets

    def update_all(self) -> None:
        """Update candles for all markets permanently."""
        while True:
            for market, period in itertools.product(self.market_list, self.periods):
                self._update_candles(market=market, period=period)

                print(f"[UPDATED] - {market} - {period}")

    def load_candle_data(self, market: str, period: str) -> pd.DataFrame:
        """Load the lastest candle data."""
        dir_path = self._update_candles(market=market, period=period)

        fnames = sorted(dir_path.iterdir(), reverse=True)
        import pdb

        pdb.set_trace()
        return pd.concat(
            [pd.read_parquet(fname) for fname in fnames], ignore_index=True
        )

    def _update_candles(self, market: str, period: str) -> Path:
        """Parse all candle data and dump them."""
        data = self._request_new_candles(market=market, period=period)
        # delete a lastest one if it exists
        dir_path = self._get_market_directory(market=market, period=period)
        if any(dir_path.iterdir()):
            sorted(dir_path.iterdir())[-1].unlink()

        # update the lastest candle data
        self._dump_data(data=data, dir_path=dir_path)
        return dir_path

    def _request_new_candles(self, market: str, period: str) -> pd.DataFrame:
        """Request the lastest data."""
        from_when = self._get_lastest_time(market=market, period=period)
        unit, sub_unit = self._get_units_from_period(period)

        # make a url to request
        url = OHLCV_URL + f"/{unit}"
        if unit == "minutes":
            url += f"/{sub_unit}"

        # comptue count interval
        interval = 60
        if unit == "minutes":
            interval *= sub_unit
        elif unit == "days":
            interval *= 60 * 24
        elif unit == "weeks":
            interval *= 60 * 24 * 7

        # get candle data until today
        to_date = datetime.today()

        data = []
        headers = {"accept": "application/json"}
        params = {"market": market, "count": 200}
        while True:
            params["to"] = to_date.strftime("%Y-%m-%d %H:%M:%S")
            success_to_request, candles = utils.request_info(url, headers, params)
            assert success_to_request, "Wrong connections"

            data += candles
            if not candles or from_when >= datetime.fromisoformat(
                candles[-1]["candle_date_time_utc"]
            ):
                break

            # Upbit api only allow 30 times for each second
            time.sleep(0.05)
            to_date -= timedelta(seconds=params["count"] * interval)

        data = pd.DataFrame.from_dict(data)
        return data[pd.to_datetime(data["candle_date_time_utc"]) > from_when]

    def _dump_data(self, data: pd.DataFrame, dir_path: Path) -> None:
        """Make data to multiple chunks and save them."""
        chunks = [
            data.iloc[i : i + self.CHUNK_SIZE]
            for i in range(0, len(data), self.CHUNK_SIZE)
        ]
        for chunk in chunks:
            end_time = chunk["candle_date_time_utc"].iloc[0]
            start_time = chunk["candle_date_time_utc"].iloc[-1]
            chunk.to_parquet(path=dir_path / f"{start_time} - {end_time}.parquet")

    def _get_lastest_time(self, market: str, period: str) -> datetime:
        """Get the lastest time of cached data."""
        dir_path = self._get_market_directory(market=market, period=period)
        fnames = sorted(dir_path.iterdir())

        # we need to request from the first
        if not fnames:
            return datetime.min

        from_when = pd.read_parquet(fnames[-1]).iloc[-1]["candle_date_time_utc"]
        from_when = datetime.strptime(from_when, "%Y-%m-%dT%H:%M:%S") - timedelta(
            seconds=1
        )
        return from_when

    def _get_units_from_period(self, period: str) -> tuple[str, Optional[int]]:
        """Get unit (and sub-unit) from period."""
        unit_info = period.split(" ")

        # n minutes
        if len(unit_info) == 1:
            return unit_info[0], None

        # days, weeks
        return unit_info[-1], int(unit_info[0])

    def _get_market_directory(self, market: str, period: str) -> Path:
        """Get a data path of the given market with period."""
        dir_path = DATA_PATH / market / period
        dir_path.mkdir(exist_ok=True, parents=True)
        return dir_path


if __name__ == "__main__":
    # dataloader = UpbitDataLoader()
    # dataloader.load_candle_data(dataloader.market_list[0], dataloader.periods[0])

    UpbitDataLoader().update_all()
