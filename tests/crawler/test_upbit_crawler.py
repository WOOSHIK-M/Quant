from quant.crawler.upbit_crawler import UpbitCrawler


class TestUpbitCrawler:

    def test_there_is_market_for_crawl(self):
        """Test that there is market for crawling."""
        # Given
        upbit_crawler = UpbitCrawler()

        # When
        markets = upbit_crawler.markets

        # Then
        assert markets is not None

    def test_there_is_period_for_crawl(self):
        """Test that there is period for crawling."""
        # Given
        upbit_crawler = UpbitCrawler()

        # When
        periods = upbit_crawler.periods

        # Then
        assert periods is not None

    def test_crawler_craw_max_request_per_second_times_max_data_count(self):
        """Test that every market and period is valid for crawling candle stick data.

        Notes:
            This will take a 1sec to finish.
        """
        # Given
        upbit_crawler = UpbitCrawler()

        # When
        market = upbit_crawler.markets[0]
        period = upbit_crawler.periods[0]

        data = upbit_crawler.crawl(market, period)

        # Then
        assert data.shape[0] == 1000
