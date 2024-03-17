from abc import ABC, abstractmethod

import pandas as pd

from quant.logger.logger import LoggerFactory


class Crawler(ABC):
    """Crawler is an abstract class for crawling candle stick data from the market."""

    logger = LoggerFactory.make_logger("Crawler")

    @property
    @abstractmethod
    def markets(self) -> tuple[str, ...]:
        """Get all available markets."""
        pass

    @property
    @abstractmethod
    def periods(self) -> tuple[str, ...]:
        """Get all available candle periods."""
        pass

    def crawl(self, market: str, period: str) -> pd.DataFrame:
        """Crawl the candle stick data from the market in period."""
        if market not in self.markets:
            raise ValueError(f"Market {market} is not available.")

        if period not in self.periods:
            raise ValueError(f"Period {period} is not available.")

        return self._crawl(market, period)

    @abstractmethod
    def _crawl(self, market: str, period: str) -> pd.DataFrame:
        """Crawl the candle stick data from the market in period."""
        pass
