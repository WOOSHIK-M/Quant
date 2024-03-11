import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import utils as utils
from contents.cache import CacheMemory
from data_miner import UpbitCandleMiner
from plotly.subplots import make_subplots
from structure import Market


class BackTestingManager(CacheMemory):
    """A manager to back-test."""

    name = "BackTesting"
    icon = "bar-chart-line"

    def __init__(self) -> None:
        """Initialize."""
        self.markets = [Market(**market) for market in utils.get_all_markets()]
        self.market_names = [market.name for market in self.markets]

        self.candle_miner = UpbitCandleMiner()

    def run(self) -> None:
        """Run a back-testing page."""
        market_name, period = self._init_page()
        self._display_candle_chart(market_name, period)

    def _init_page(self) -> tuple[str, str]:
        """Initialize a page."""
        st.title("Dashboard")

        market_name = st.selectbox(label="markets", options=self.market_names)
        period = st.selectbox(label="period", options=self.candle_miner.periods)
        return market_name, period

    def _display_candle_chart(self, market_name: str, period: str) -> None:
        """Call and draw the candle chart."""
        market_code = Market.get_code_from_name(market_name)
        candles = self.candle_miner.load_candle_data(market_code, period)
        st.plotly_chart(self._draw_ohlcv(candles), use_container_width=True)

    def _draw_ohlcv(self, data: pd.DataFrame) -> go.Figure:
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
