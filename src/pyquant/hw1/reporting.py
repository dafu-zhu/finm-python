import numpy as np
import polars as pl


def value_tbl(time: list, value: list) -> pl.LazyFrame:
    tb = pl.LazyFrame({'time': time, 'value': value})
    tb = tb.with_columns(
        pl.col('time').cast(pl.Datetime), pl.col('value').cast(pl.Float64))
    return tb


def total_return(value: list) -> float:
    return value[-1] / value[0] - 1


def period_returns(time: list, value: list) -> pl.LazyFrame:
    tb = value_tbl(time, value)
    tb = tb.with_columns(
        pl.col('value').pct_change().alias('returns')
    ).drop_nulls()
    return tb


def calc_sharpe(value: list, risk_free: float = 0) -> float:
    s = pl.Series('value', value)
    pct_chg = s.pct_change().drop_nulls()
    excess_ret = pct_chg.mean() - risk_free
    volatility = pct_chg.std()
    return excess_ret / volatility


def calc_max_dd(time: list, value: list) -> dict:  # @save
    """
    Calculate maximum drawdown for an asset
    :param time
    :param value: portfolio's value

    Returns
    -------
    Dict:
        - max_drawdown: amount
        - peak: day that reaches peak of the max drawdown
        - bottom: day that reaches bottom of the max drawdown
        - recover: day recover, if no, then "nan"
        - duration: time length to recover, if no, then "nan"
        - drawdown (pl.LazyFrame): drawdown time series
    """
    # create new df, calculate cumulative return, peak, bottom
    tb = period_returns(time, value)
    tb = tb.with_columns(
        (pl.col('returns') + 1).cum_prod().alias('cum_return')
    ).with_columns(
        pl.col("cum_return").cum_max().alias("peak")
    ).with_columns(
        (pl.col("cum_return") / pl.col("peak") - 1).alias("drawdown")
    )

    # filter the period where max drawdown is realized
    dd_period = tb.filter(
        pl.col("drawdown").eq(pl.col("drawdown").min())
    ).collect()
    max_dd = dd_period["drawdown"][0]
    peak_value = dd_period["peak"]
    bottom_day = dd_period['time'][0]

    peak_day = tb.filter(
        (pl.col("cum_return").eq(peak_value)) &
        (pl.col('time').le(bottom_day))
    ).collect()['time'][-1]  # Take the last occurrence before bottom

    recover_df = tb.filter(
        pl.col("cum_return").ge(peak_value)
        & (pl.col('time').gt(bottom_day))
    ).collect()
    if recover_df.height > 0:
        recover_day = recover_df[0]['time'][0]
        duration = recover_day - peak_day
    else:
        recover_day = None
        duration = None

    result = {
        "max_drawdown": max_dd,
        "peak": peak_day,
        "bottom": bottom_day,
        "recover": recover_day,
        "duration": duration,
        "drawdown": tb.select(pl.col(['time', "drawdown"]))
    }
    return result