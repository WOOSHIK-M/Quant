import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import src.utils as utils
from src.pages.cache import CacheMemory
from src.structure import Market

UPBIT_OPEN_API_MARKET_URL = "https://api.upbit.com/v1/market"
OHLCV_URL = "https://api.upbit.com/v1/candles"


class ChartHandler:
    """Get chart information from Upbit."""

    @property
    def periods(self) -> list[str]:
        """Get all candle types."""
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

    def get_candlesticks(self, market_code: str, period: str) -> pd.DataFrame:
        """Get candles sticks according to the given period."""
        info = period.split(" ")
        if len(info) == 1:
            unit, sub_unit = info[0], None
        else:
            unit, sub_unit = info[-1], int(info[0])

        data = self._request_candle_sticks(
            market_code=market_code,
            unit=unit,
            sub_unit=sub_unit,
            from_when=datetime.min,
        )
        return data

    def _request_candle_sticks(
        self,
        market_code: str,
        unit: str,
        sub_unit: int,
        from_when: datetime,
    ) -> pd.DataFrame:
        """."""
        url = OHLCV_URL + f"/{unit}"
        if unit == "minutes":
            url += f"/{sub_unit}"

        # compute count interval
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
            success_to_request, candles = utils.request_info(
                url=url, headers=headers, params=params
            )
            assert success_to_request

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

    def draw(self, data: pd.DataFrame) -> go.Figure:
        """Draw candle chart."""
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.3,
            subplot_titles=("Chart", "Volume"),
            row_heights=[0.9, 0.1],
        )

        # draw ohcl
        go_ohcl = go.Candlestick(
            x=data["candle_date_time_kst"],
            open=data["opening_price"],
            high=data["high_price"],
            low=data["low_price"],
            close=data["trade_price"],
            name="Price",
            increasing_line_color="red",
            decreasing_line_color="blue",
            showlegend=False,
        )
        fig.add_trace(go_ohcl, row=1, col=1)

        # draw volumes
        go_volumes = go.Bar(
            x=data["candle_date_time_kst"],
            y=data["candle_acc_trade_volume"],
            showlegend=False,
        )
        fig.add_trace(go_volumes, row=2, col=1)

        # plot!
        fig.update_yaxes(fixedrange=False)
        # fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update_layout(height=600)
        return fig


class BackTestingManager(CacheMemory):
    """A manager to back-test."""

    name = "BackTesting"
    icon = "bar-chart-line"

    def __init__(self) -> None:
        """Initialize."""
        self.chart_handler = ChartHandler()

        # get all markets
        self.market_infos = self._get_market_infos()
        self.market_list = self.market_infos.keys()

    def run(self) -> None:
        """Run a back-testing page."""
        market, period = self.init_page()

        # draw a candle chart
        if st.button("Load"):
            self.display_candle_chart(market, period)

    def init_page(self) -> tuple[str, str]:
        """Initialize a page."""
        st.title("Dashboard")

        selected_market = st.selectbox(label="markets", options=self.market_list)
        period = st.selectbox(label="period", options=self.chart_handler.periods)
        return selected_market, period

    def display_candle_chart(self, market: str, period: str) -> None:
        """Call and draw the candle chart."""
        market_code = Market.resolve_key(market)
        data = self.chart_handler.get_candlesticks(
            market_code=market_code, period=period
        )
        st.plotly_chart(self.chart_handler.draw(data), use_container_width=True)

    def _get_market_infos(self) -> dict[str, Market]:
        """Get all markets from Upbit."""
        _, market_info = utils.request_info(url=UPBIT_OPEN_API_MARKET_URL + "/all")

        markets = [Market(**info) for info in market_info]
        return {market.key: market for market in markets}
