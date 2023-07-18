from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.structure import Market


def draw_ohclv(data: pd.DataFrame, market: Market, fname: str | Path = "./candle.png") -> None:
    """Draw candle chart."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("OHCL", "Volume"),
        row_width=[0.2, 0.7],
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
    fig.update_layout(title=dict(text=market.english_name, font=dict(size=30)))
    fig.show()
