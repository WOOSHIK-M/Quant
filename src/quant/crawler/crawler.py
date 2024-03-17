from abc import ABC, abstractmethod

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

    def crawl(self, market: str, period: str) -> None:
        """Crawl the candle stick data from the market in period."""
        if market not in self.markets:
            Crawler.logger.error(f"Market {market} is not available.")
            return
        if period not in self.periods:
            Crawler.logger.error(f"Period {period} is not available.")
            return

        return self._crawl(market, period)

    @abstractmethod
    def _crawl(self, market: str, period: str) -> None:
        """Crawl the candle stick data from the market in period."""
        pass
