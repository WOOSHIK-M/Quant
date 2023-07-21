from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

from src.structure import Market


def make_dashboard(data: pd.DataFrame, market: Market, fname: str | Path = "./candle.png") -> None:
    """Use dash."""
    app = Dash(__name__)
    app.layout = html.Div(
        children=[
            html.H3(children="Back Testing Dash Board"),
            # html.Div(children="""docstring"""),
            # html.H4('Test Plot'),
            dcc.Graph(
                id="graph",
                # style={'width': '180vh', 'height': '90vh'},
            ),
            # html.P("Height"),
            # dcc.Slider(
            #     id="slider-width",
            #     min=.1,
            #     max=.9,
            #     value=0.2,
            #     step=0.1
            # ),
            # dcc.Checklist(
            #     id='toggle-rangeslider',
            #     options=[
            #         {
            #             'label': 'Include Rangeslider',
            #             'value': 'slider'
            #         }
            #     ],
            #     value=['slider']
            # ),
        ]
    )

    @app.callback(Output("graph", "figure"), Input("slider-width", "value"))
    def inner_method(height: float):
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=("OHCL", "Volume"),
            row_width=[height, 1 - height],
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
        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.update_layout(
            title=dict(
                text=market.english_name,
                # font=dict(size=20),
            ),
            # width=3200,
            height=2160,
        )
        fig.update_yaxes(automargin=True)
        return fig

    app.run_server(debug=True)


def draw_ohclv(data: pd.DataFrame) -> go.Figure:
    """Draw candle chart."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Chart", "Volume"),
        row_heights=[0.7, 0.3],
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
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(height=1600)
    # fig.update_layout(title=dict(text=str(market), font=dict(size=30)))
    # fig.show()
    return fig
