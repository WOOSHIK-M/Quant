import datetime
from abc import ABCMeta, abstractmethod
from typing import Any

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

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

    def show(self) -> html.Div:
        """."""
        options = list(self.d_markets.keys())
        contents = dbc.Row(
            children=[
                dbc.Col(children=html.Div(dcc.Graph(id="ohclv_graph")), width=10),
                dbc.Col(
                    children=[
                        # select market code
                        html.Label("Market codes"),
                        dcc.Dropdown(id="market", options=options, value=options[0]),
                        # date picker
                        html.Br(),
                        html.Label("Datetime"),
                        self._get_date_picker(),
                    ],
                    width=2,
                ),
            ],
        )
        return contents

    def _get_date_picker(self) -> html.Div:
        """Get a date picker."""
        today = datetime.datetime.today()
        return dmc.DateRangePicker(
            id="date-range-picker",
            description="description.",
            minDate=datetime.date(1995, 3, 5),
            value=[today - datetime.timedelta(days=200), today],
        )

    def _get_ohclv_figure(self, market_name: str) -> go.Figure:
        """Get ohclv chart."""
        market_code = self.d_markets[market_name]

        # if it is not in cache, get candles
        if market_code not in self._cache:
            data = self.client.get_day_candles(market_code=market_code)
            self._cache[market_code] = data
        data = self._cache[market_code]
        return utils.draw_ohclv(data)

    def _call_rendering_function(self, app: Dash) -> None:
        """Render ohlcv chart."""

        @app.callback(
            Output(component_id="ohclv_graph", component_property="figure"),
            Input(component_id="market", component_property="value"),
        )
        def _render_ohclv_chart(market_name: str) -> go.Figure:
            """Render chart of the given market name."""
            return self._get_ohclv_figure(market_name)
