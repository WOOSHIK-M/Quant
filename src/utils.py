from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def draw_ohclv(
    data: pd.DataFrame,
    moving_averages: list[int] = [5, 20, 60, 120, 200],
    n_ticks: int = None,
    start_date: date = None,
    end_date: date = None,
) -> go.Figure:
    """Draw candle chart."""
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Chart", "Volume"),
        row_heights=[0.8, 0.2],
    )

    # update moving averages
    ma_col_name = "moving_average_{moving_average}"
    for moving_average in moving_averages:
        ma_data = data["trade_price"][::-1].rolling(window=moving_average, min_periods=1).mean()
        data[ma_col_name.format(moving_average=moving_average)] = ma_data[::-1]

    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        data = data[pd.to_datetime(data["candle_date_time_kst"]) <= end_date]

    if n_ticks:
        data = data[-n_ticks:]
    elif start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        data = data[pd.to_datetime(data["candle_date_time_kst"]) >= start_date]

    # draw moving average
    for moving_average in moving_averages:
        line = go.Scatter(
            x=data["candle_date_time_kst"],
            y=data[ma_col_name.format(moving_average=moving_average)],
            line=dict(width=3),
            name=f"{moving_average}",
        )
        fig.add_trace(line, row=1, col=1)

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
