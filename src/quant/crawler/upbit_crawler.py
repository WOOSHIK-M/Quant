from datetime import datetime, timedelta
from time import sleep

import polars
import pandas as pd

import quant.utils as utils
from quant.crawler.crawler import Crawler


class UpbitCrawler(Crawler):
    """Crawl Upbit coin candlestick data using Upbit API."""

    def __init__(self):
        # URLs
        self.__UPBIT_MARKET_API_URL = "https://api.upbit.com/v1/market"
        self.__UPBIT_CANDLE_API_URL = "https://api.upbit.com/v1/candles"

        # Constants
        self.__MAX_REQUEST_PER_SECOND = 5
        self.__MAX_DATA_COUNT_PER_REQUEST = 200

        # Display-name: (api, minutes)
        self.__periods: dict[str, tuple[str, int]] = {
            "1 minutes": ("minutes/1", 1),
            "3 minutes": ("minutes/3", 3),
            "5 minutes": ("minutes/5", 5),
            "10 minutes": ("minutes/10", 10),
            "15 minutes": ("minutes/15", 15),
            "30 minutes": ("minutes/30", 30),
            "60 minutes": ("minutes/60", 60),
            "240 minutes": ("minutes/240", 240),
            "days": ("days", 60 * 24),
            "weeks": ("weeks", 60 * 24 * 7),
        }
        super().__init__()

    @property
    def periods(self) -> tuple[str, ...]:
        """Get all available candle periods."""
        return tuple(self.__periods.keys())

    @property
    def markets(self) -> tuple[str, ...]:
        """Get all available markets."""
        _, markets = utils.request_info(url=self.__UPBIT_MARKET_API_URL + "/all")
        return tuple(market["market"] for market in markets)

    def _crawl(self, market: str, period: str) -> pd.DataFrame:
        """Crawl the candle stick data from the market in period."""
        unit, minutes = self.__periods[period]
        url = f"{self.__UPBIT_CANDLE_API_URL}/{unit}"

        target_datetime = datetime.today()
        data = []
        for _ in range(self.__MAX_REQUEST_PER_SECOND * 2):
            data += self.__request_candlestick(url, market, target_datetime)
            target_datetime -= timedelta(minutes=minutes * self.__MAX_DATA_COUNT_PER_REQUEST)
        result = polars.from_dicts(data).to_pandas()
        return result

    def __request_candlestick(self, url, market, time) -> list:
        """Request candlestick data from Upbit."""
        params = {
            "market": market,
            "count": self.__MAX_DATA_COUNT_PER_REQUEST,
            "to": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        while True:
            success_to_request, candles = utils.request_info(
                url=url,
                headers={"accept": "application/json"},
                params=params,
            )
            assert success_to_request, f"Wrong connections - {url}, params: {params}"
            if len(candles) == self.__MAX_DATA_COUNT_PER_REQUEST:
                break

            # If the data is not enough, retry after 0.5 seconds.
            # This is because Upbit API has a limit of 5 requests per second.
            # There is no criteria for waiting time, so I just set 0.5 seconds.
            self.logger.warning(f"Failed to get enough data. Retry after 0.5 seconds.")
            self.logger.warning(f"Message: {candles}")
            sleep(0.5)
        return candles
