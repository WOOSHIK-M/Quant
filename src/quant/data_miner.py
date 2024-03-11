import itertools
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import utils as utils
from api_urls import OHLCV_URL
from redis_connector import redis_client

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True)


class UpbitCandleMiner:
    """Request candles and dump them to local device."""

    TASK_QUEUE = "queue"
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
    def markets(self) -> list[str]:
        """Get all available markets."""
        return [market["market"] for market in utils.get_all_markets()]

    @staticmethod
    def make_task(market: str, period: str) -> str:
        """Make a task to put redis."""
        return f"{market}/{period}"

    def run(self) -> None:
        """Get all candles for all markets permanently."""
        if self.TASK_QUEUE in redis_client.keys():
            redis_client.delete(self.TASK_QUEUE)

        market_lst = [
            self.make_task(market, period)
            for market, period in itertools.product(self.markets, self.periods)
        ]
        redis_client.lpush(self.TASK_QUEUE, *market_lst)
        while True:
            market, period = redis_client.lpop(self.TASK_QUEUE).decode("utf-8").split("/")
            print(f"[Loading]  - {market} / {period}", end=" - ")
            self._update_candles(market=market, period=period)

            redis_client.rpush(self.TASK_QUEUE, self.make_task(market, period))
            time.sleep(0.3)

    def load_candle_data(self, market: str, period: str) -> pd.DataFrame:
        """Load candle data."""
        dir_path = self._get_market_directory(market=market, period=period)

        task = self.make_task(market, period)
        redis_client.lpush(self.TASK_QUEUE, task)
        while not list(dir_path.iterdir()):
            print("Loading...", market)
            time.sleep(0.1)

        # get the newly dumped data
        fnames = sorted(dir_path.iterdir())
        return pd.concat([pd.read_parquet(fname) for fname in fnames])

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
        """Request the lastest data.

        Procedures:
            1. get the lastest time of the already dumped data (if exists).
            2. request new candles until the current timestamp.
            3. concat the new candles to the old one.
        """
        cached_data, from_when = self._get_lastest_time(market=market, period=period)
        unit, sub_unit = self._get_units_from_period(period)

        # make a url to request
        url = OHLCV_URL + f"/{unit}"
        if unit == "minutes":
            url += f"/{sub_unit}"

        # comptue count interval
        interval = 1
        if unit == "minutes":
            interval *= sub_unit
        elif unit == "days":
            interval *= 60 * 24
        elif unit == "weeks":
            interval *= 60 * 24 * 7

        # get candle data until today
        data = []
        to_date = datetime.today()
        while True:
            success_to_request, candles = utils.request_info(
                url=url,
                headers={"accept": "application/json"},
                params={
                    "market": market,
                    "count": 200,
                    "to": to_date.strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            assert success_to_request, "Wrong connections"

            data += candles
            try:
                if not candles or from_when >= datetime.fromisoformat(
                    candles[-1]["candle_date_time_utc"]
                ):
                    break
            # TODO : Remove this!
            except Exception:
                import pdb

                pdb.set_trace()

            to_date -= timedelta(minutes=200 * interval)

        data = pd.DataFrame.from_dict(data)
        data = data[pd.to_datetime(data["candle_date_time_utc"]) > from_when]
        return pd.concat([data, cached_data], ignore_index=True)

    def _dump_data(self, data: pd.DataFrame, dir_path: Path) -> None:
        """Make data to multiple chunks and save them."""
        chunks = [
            data.iloc[::-1][i : i + self.CHUNK_SIZE] for i in range(0, len(data), self.CHUNK_SIZE)
        ]
        for chunk in chunks:
            start_time = chunk["candle_date_time_utc"].iloc[0]
            end_time = chunk["candle_date_time_utc"].iloc[-1]
            chunk.iloc[::-1].to_parquet(path=dir_path / f"{start_time} - {end_time}.parquet")

    def _get_lastest_time(self, market: str, period: str) -> tuple[pd.DataFrame, datetime]:
        """Get the lastest time of cached data."""
        dir_path = self._get_market_directory(market=market, period=period)
        fnames = sorted(dir_path.iterdir())

        # we need to request from the first
        if not fnames:
            return pd.DataFrame(), datetime.min

        cached_data = pd.read_parquet(fnames[-1])
        from_when = cached_data.iloc[-1]["candle_date_time_utc"]
        from_when = datetime.strptime(from_when, "%Y-%m-%dT%H:%M:%S")
        return cached_data.iloc[::-1], from_when + timedelta(seconds=1)

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
