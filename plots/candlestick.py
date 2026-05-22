import datetime as dt
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from plots.utils import set_plot_theme

try:
    import mplfinance as mpf
    MPLFINANCE_AVAILABLE = True
except ImportError:
    MPLFINANCE_AVAILABLE = False
    mpf = None

# Ticker -> display label for symbol autocomplete
SYMBOL_CHOICES = {
    "AAPL": "Apple (AAPL)",
    "TSLA": "Tesla (TSLA)",
    "AMZN": "Amazon (AMZN)",
    "GOOGL": "Google (GOOGL)",
    "MSFT": "Microsoft (MSFT)",
    "NVDA": "NVIDIA (NVDA)",
    "META": "Meta (META)",
    "NFLX": "Netflix (NFLX)",
    "AMD": "AMD (AMD)",
    "INTC": "Intel (INTC)",
}

# Range keys for fetch logic; labels use plain time phrases (Stocks app style)
CANDLESTICK_RANGE_CHOICES = {
    "1D": "Past 24 hours (hourly bars)",
    "1W": "Past week",
    "1M": "Past month",
    "3M": "Past 3 months",
    "6M": "Past 6 months",
    "YTD": "Year to date",
    "1Y": "Past year",
    "2Y": "Past 2 years",
    "5Y": "Past 5 years",
}
CANDLESTICK_RANGES = list(CANDLESTICK_RANGE_CHOICES.keys())
MA_PRESET_PERIODS = [10, 50, 120]  # highlighted when within chart bar count
MA_MIN_PERIOD = 2  # mplfinance requires mav periods >= 2

COMPANY_TICKERS = {label.split(" (")[0]: t for t, label in SYMBOL_CHOICES.items()}
CANDLESTICK_COMPANIES = list(COMPANY_TICKERS.keys())

TODAY = dt.date.today()
_TODAY = TODAY
CURRENT_YEAR = _TODAY.year
CURRENT_MONTH = _TODAY.month


def resolve_symbol(symbol_input: str) -> str:
    """Extract Yahoo ticker from selectize label or raw text."""
    text = (symbol_input or "").strip()
    m = re.search(r"\(([A-Za-z]{1,6})\)\s*$", text)
    if m:
        return m.group(1).upper()
    return text.upper()


def max_ma_period(n_bars: int) -> int:
    """Largest moving-average window allowed for n_bars of OHLC data."""
    return max(0, n_bars)


def ma_period_choices(n_bars: int) -> List[str]:
    """All MA periods that can be computed for this chart (mplfinance: 2..n_bars)."""
    cap = max_ma_period(n_bars)
    if cap < MA_MIN_PERIOD:
        return []
    return [str(p) for p in range(MA_MIN_PERIOD, cap + 1)]


def validate_ma_periods(
    periods: List[int], n_bars: int
) -> Tuple[List[int], Optional[str]]:
    """Keep valid periods (>= 2 and <= bar count)."""
    if not periods:
        return [], None
    cap = max_ma_period(n_bars)
    if cap < MA_MIN_PERIOD:
        return [], "Not enough data points to add a moving average."
    valid = sorted(
        {int(x) for x in periods if MA_MIN_PERIOD <= int(x) <= cap}
    )
    return valid, None


def _format_day_label(d: dt.date) -> str:
    return f"{d.strftime('%A')}, {d.strftime('%B')} {d.day}, {d.year}"


def _exclusive_end(d: dt.date) -> str:
    return (d + dt.timedelta(days=1)).isoformat()


def _range_window(range_key: str) -> Tuple[dt.date, dt.date, str, bool]:
    """Start (inclusive), exclusive end date, yfinance interval, include time in labels."""
    end = _TODAY
    if range_key == "1D":
        return end - dt.timedelta(days=2), end + dt.timedelta(days=1), "5m", True
    if range_key == "1W":
        return end - dt.timedelta(days=7), end + dt.timedelta(days=1), "1h", True
    if range_key == "1M":
        return end - dt.timedelta(days=30), end + dt.timedelta(days=1), "1d", False
    if range_key == "3M":
        return end - dt.timedelta(days=90), end + dt.timedelta(days=1), "1d", False
    if range_key == "6M":
        return end - dt.timedelta(days=180), end + dt.timedelta(days=1), "1d", False
    if range_key == "YTD":
        return dt.date(end.year, 1, 1), end + dt.timedelta(days=1), "1d", False
    if range_key == "1Y":
        return end - dt.timedelta(days=365), end + dt.timedelta(days=1), "1d", False
    if range_key == "2Y":
        return end - dt.timedelta(days=365 * 2), end + dt.timedelta(days=1), "1d", False
    if range_key == "5Y":
        return end - dt.timedelta(days=365 * 5), end + dt.timedelta(days=1), "1d", False
    raise ValueError(f"Unknown range: {range_key}")


def _hist_to_ohlcv_dict(hist: pd.DataFrame, include_time: bool = False) -> Dict[str, List]:
    hist = hist.copy()
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)

    hist = hist.reset_index()
    date_col = "Date" if "Date" in hist.columns else hist.columns[0]
    hist["Date"] = pd.to_datetime(hist[date_col])
    if include_time:
        fmt = "%Y-%m-%d %H:%M"
        dates = hist["Date"].dt.strftime(fmt).tolist()
    else:
        dates = hist["Date"].dt.strftime("%Y-%m-%d").tolist()

    return {
        "Date": dates,
        "Open": hist["Open"].round(2).tolist(),
        "High": hist["High"].round(2).tolist(),
        "Low": hist["Low"].round(2).tolist(),
        "Close": hist["Close"].round(2).tolist(),
        "Volume": hist["Volume"].fillna(0).astype(int).tolist(),
    }


def fetch_stock_by_range(symbol: str, range_key: str) -> Tuple[Dict[str, List], str]:
    import yfinance as yf

    ticker_symbol = resolve_symbol(symbol)
    if not ticker_symbol:
        raise ValueError("Enter a stock symbol (e.g. AAPL).")

    ticker = yf.Ticker(ticker_symbol)
    if range_key == "1D":
        hist = ticker.history(period="5d", interval="5m", auto_adjust=True)
        if hist is not None and not hist.empty:
            cutoff = pd.Timestamp.now(tz=hist.index.tz) - pd.Timedelta(hours=24)
            hist = hist[hist.index >= cutoff]
        include_time = True
    else:
        start, end, interval, include_time = _range_window(range_key)
        hist = ticker.history(
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            auto_adjust=True,
        )

    subtitle = CANDLESTICK_RANGE_CHOICES.get(range_key, range_key)
    if range_key == "1W":
        subtitle += " (hourly bars)"
    elif range_key not in ("1D", "YTD"):
        subtitle += " (daily bars)"

    if hist is None or hist.empty:
        raise ValueError(f"No data for {ticker_symbol} ({range_key}).")
    return _hist_to_ohlcv_dict(hist, include_time=include_time), subtitle


def generate_stock_data(
    symbol: str = "TSLA",
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31",
    seed: Optional[int] = 42,
) -> Dict[str, List]:
    if seed is not None:
        np.random.seed(seed)

    company_params = {
        "TSLA": {"start_price": 200.0, "volatility": 0.025},
        "AAPL": {"start_price": 150.0, "volatility": 0.020},
        "GOOGL": {"start_price": 140.0, "volatility": 0.022},
        "AMZN": {"start_price": 120.0, "volatility": 0.024},
    }
    sym = resolve_symbol(symbol)
    params = company_params.get(sym, {"start_price": 100.0, "volatility": 0.022})
    start_price = params["start_price"]
    volatility = params["volatility"]

    all_dates = pd.date_range(start=start_date, end=end_date)
    trading_dates = all_dates[all_dates.dayofweek < 5]
    dates = [d.strftime("%Y-%m-%d") for d in trading_dates]

    opens, closes, highs, lows, volumes = [], [], [], [], []
    for i, _ in enumerate(dates):
        opens.append(start_price if i == 0 else closes[i - 1])
        price_change = np.random.normal(0, volatility * opens[i])
        close = opens[i] + price_change
        closes.append(round(close, 2))
        daily_range = abs(price_change) + volatility * opens[i]
        highs.append(round(max(opens[i], close) + abs(np.random.normal(0, daily_range / 3)), 2))
        lows.append(round(min(opens[i], close) - abs(np.random.normal(0, daily_range / 3)), 2))
        volumes.append(int(1_000_000 * np.random.uniform(0.7, 1.3)))

    return {"Date": dates, "Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes}


def draw_candlestick_fallback(ax, ohlc_data, width=0.6, colorup="g", colordown="r"):
    for date_num, open_price, high, low, close in ohlc_data:
        color = colorup if close >= open_price else colordown
        line_width = max(1, width / 30) if width > 10 else 1
        ax.plot([date_num, date_num], [low, high], color="black", linewidth=line_width)
        height = abs(close - open_price)
        bottom = min(open_price, close)
        rect = plt.Rectangle(
            (date_num - width / 2, bottom), width, max(height, 0.01),
            facecolor=color, edgecolor="black", alpha=0.8, linewidth=line_width,
        )
        ax.add_patch(rect)


def _draw_ma_lines(ax, df: pd.DataFrame, periods: List[int], theme: str):
    colors = ["#1f77b4", "#ff7f0e", "#9467bd", "#2ca02c", "#d62728"]
    for i, period in enumerate(periods):
        ma = df["Close"].rolling(window=period, min_periods=period).mean()
        ax.plot(
            df["Date"], ma,
            label=f"MA {period}",
            color=colors[i % len(colors)],
            linewidth=1.5,
        )
    if periods:
        ax.legend(loc="upper left", fontsize=9)


def create_candlestick_plot(
    data_dict: Dict[str, List],
    symbol: str = "TSLA",
    theme: str = "Light",
    range_label: str = "",
    data_source: str = "Yahoo Finance",
    ma_periods: Optional[List[int]] = None,
    **_kwargs,
) -> plt.Axes:
    if not data_dict["Date"]:
        raise ValueError("No data points to plot.")

    df = pd.DataFrame(data_dict)
    df["Date"] = pd.to_datetime(df["Date"])
    ticker = resolve_symbol(symbol)
    ma_periods = [p for p in (ma_periods or []) if p >= MA_MIN_PERIOD]

    title = f"Candlestick: {ticker}"
    if range_label:
        title += f" — {range_label}"

    if MPLFINANCE_AVAILABLE:
        mpf_df = df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]
        if theme == "Dark":
            style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})

        plot_kwargs = dict(
            type="candle",
            volume=False,
            returnfig=True,
            style=style,
            title=title,
            ylabel="Price ($)",
            figsize=(12, 6),
            warn_too_much_data=10000,
        )
        if ma_periods:
            plot_kwargs["mav"] = tuple(ma_periods)

        fig, axes = mpf.plot(mpf_df, **plot_kwargs)
        ax = axes[0] if isinstance(axes, (list, tuple)) else axes
        set_plot_theme(fig, ax, theme)
        fig.text(
            0.5, 0.01,
            f"{data_source} · Real market OHLC (split/dividend adjusted) · ~15 min delayed · Not for trading",
            ha="center", fontsize=8, style="italic", color="gray",
        )
        fig.tight_layout(rect=[0, 0.03, 1, 1])
        return ax

    df["Date_num"] = df["Date"].apply(mdates.date2num)
    ohlc = df[["Date_num", "Open", "High", "Low", "Close"]].values
    fig, ax = plt.subplots(figsize=(12, 6))
    set_plot_theme(fig, ax, theme)
    draw_candlestick_fallback(ax, ohlc, width=0.6)
    if ma_periods:
        _draw_ma_lines(ax, df, ma_periods, theme)
    ax.xaxis_date()
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    return ax


def create_candlestick(
    symbol: str,
    range_key: str,
    theme: str,
    ma_periods: Optional[List[int]] = None,
) -> Tuple[plt.Axes, int, Optional[str]]:
    """Returns axes, bar count, and optional MA validation message."""
    data_source = "Yahoo Finance"
    range_label = ""
    try:
        data, range_label = fetch_stock_by_range(symbol, range_key)
    except Exception as e:
        print(f"Live stock fetch failed ({e}); using synthetic fallback.")
        data_source = "Sample data (Yahoo Finance unavailable)"
        start, end, _, _ = _range_window(range_key)
        data = generate_stock_data(
            symbol,
            start.isoformat(),
            (end - dt.timedelta(days=1)).isoformat(),
        )
        range_label = f"{range_key} (sample)"

    n_bars = len(data["Date"])
    valid_ma, ma_err = validate_ma_periods(ma_periods or [], n_bars)

    ax = create_candlestick_plot(
        data,
        symbol=symbol,
        theme=theme,
        range_label=range_label,
        data_source=data_source,
        ma_periods=valid_ma,
    )
    return ax, n_bars, ma_err
