from abc import ABCMeta, abstractmethod
from typing import Any

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from dash.development.base_component import Component

import src.utils as utils
from src.client import UpbitClient


class Page(metaclass=ABCMeta):
    """Base page class."""

    def __init__(self, app: Dash) -> None:
        """Initialize.

        If you have some rendering contents, have to customize the method.
        """
        self._call_rendering_function(app)

    @abstractmethod
    def _call_rendering_function(self, app: Dash) -> Any:
        """Initialize rendering function."""
        pass


class ChartHandler(Page):
    """Show charts."""

    def __init__(self, app) -> None:
        """Initialize."""
        self.client = UpbitClient()
        self.d_markets = {str(m): m.market for m in self.client.markets.values()}

        # cache memory to speed up of loading charts
        self._cache = dict()

        super().__init__(app)

    def show(self) -> Component:
        """."""
        contents = dbc.Row(
            children=[
                dbc.Col(children=html.Div(dcc.Graph(id="ohclv_graph")), width=10),
                dbc.Col(
                    children=[
                        *self._select_market_codes(),
                        html.Br(),
                        *self._select_candle_format(),
                    ],
                    width=2,
                ),
            ],
        )
        return contents

    def _select_market_codes(self) -> list[Component]:
        """Build a dropdown button to select another option."""
        options = list(self.d_markets.keys())
        return [
            html.Label("Market codes"),
            dcc.Dropdown(id="dropdown-market-code", options=options, value=options[0]),
        ]

    def _select_candle_format(self) -> list[Component]:
        """Build a dropdown button to select another candler format."""
        assert self.client.UNIT_OPTIONS[0] == "minutes"

        units = self.client.UNIT_OPTIONS
        options = [f"{units[0]}-{sub_unit}" for sub_unit in self.client.SUB_UNIT_OPTIONS]
        options = sorted(options, key=lambda x: int(x.split("-")[1]), reverse=True)

        options = units[1:] + options
        return [
            html.Label("Candle Size"),
            dcc.Dropdown(id="dropdown-format", options=options, value=options[0]),
        ]

    def _call_rendering_function(self, app: Dash) -> None:
        """Render ohlcv chart."""

        def _get_ohclv_figure(
            market_name: str,
            candlestick_info: str,
        ) -> go.Figure:
            """Get ohclv chart."""
            market_code = self.d_markets[market_name]

            if "-" in candlestick_info:
                unit, sub_unit = candlestick_info.split("-")
                sub_unit = int(sub_unit)
            else:
                unit, sub_unit = candlestick_info, 1

            # if it is not in cache, get candles
            key = (market_code, unit, sub_unit)
            if key not in self._cache:
                data = self.client.get_candlesticks(
                    market_code=market_code,
                    unit=unit,
                    sub_unit=sub_unit,
                )
                self._cache[key] = data
            data = self._cache[key]
            return utils.draw_ohclv(data)

        @app.callback(
            Output(component_id="ohclv_graph", component_property="figure"),
            Input(component_id="dropdown-market-code", component_property="value"),
            Input(component_id="dropdown-format", component_property="value"),
        )
        def _render_ohclv_chart(
            market_name: str,
            candlestick_info: str,
        ) -> go.Figure:
            """Render chart of the given market name."""
            return _get_ohclv_figure(market_name, candlestick_info)