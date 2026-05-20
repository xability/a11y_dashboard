import calendar
import datetime as dt
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

COMPANY_TICKERS = {
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Apple": "AAPL",
}

CANDLESTICK_COMPANIES = list(COMPANY_TICKERS.keys())
CANDLESTICK_TIMEFRAMES = ["Hourly", "Daily", "Monthly", "Yearly"]

TODAY = dt.date.today()
_TODAY = TODAY
CURRENT_YEAR = _TODAY.year
CURRENT_MONTH = _TODAY.month

# Anniversary years ending today (e.g. May 20, 2017 – May 20, 2026 when today is May 20, 2026)
YEARLY_LOOKBACK_YEARS = 9
HOURLY_LOOKBACK_DAYS = 7

CANDLESTICK_MONTHS = [
    ("January", "1"), ("February", "2"), ("March", "3"), ("April", "4"),
    ("May", "5"), ("June", "6"), ("July", "7"), ("August", "8"),
    ("September", "9"), ("October", "10"), ("November", "11"), ("December", "12"),
]
CANDLESTICK_MONTH_LABELS = {v: lbl for lbl, v in CANDLESTICK_MONTHS}
CANDLESTICK_MONTH_NAMES = [lbl for lbl, _ in CANDLESTICK_MONTHS]
CANDLESTICK_MONTH_DEFAULT = CANDLESTICK_MONTH_LABELS[str(CURRENT_MONTH)]
MONTH_NAME_TO_NUM = {lbl.lower(): int(val) for lbl, val in CANDLESTICK_MONTHS}
MONTH_NAME_TO_NUM.update({str(i): i for i in range(1, 13)})


def _format_day_label(d: dt.date) -> str:
    return f"{d.strftime('%A')}, {d.strftime('%B')} {d.day}, {d.year}"


def get_available_years() -> List[str]:
    """Years up to and including today (no future years)."""
    return [str(y) for y in range(CURRENT_YEAR, CURRENT_YEAR - 15, -1)]


CANDLESTICK_YEARS = get_available_years()


def get_available_month_names(year: int) -> List[str]:
    """Month names that have started on or before today for the given year."""
    if year > CURRENT_YEAR:
        return []
    max_month = CURRENT_MONTH if year == CURRENT_YEAR else 12
    return [CANDLESTICK_MONTH_LABELS[str(m)] for m in range(1, max_month + 1)]


def get_default_month_for_year(year: int) -> str:
    names = get_available_month_names(year)
    if not names:
        return CANDLESTICK_MONTH_DEFAULT
    if year == CURRENT_YEAR:
        return CANDLESTICK_MONTH_LABELS[str(CURRENT_MONTH)]
    return names[-1]


def build_hourly_day_choices() -> Dict[str, str]:
    """Last 7 calendar days ending today: {ISO date: label} for Shiny input_select."""
    choices = {}
    for i in range(HOURLY_LOOKBACK_DAYS - 1, -1, -1):
        d = _TODAY - dt.timedelta(days=i)
        choices[d.isoformat()] = _format_day_label(d)
    return choices


def get_hourly_day_default() -> str:
    return _TODAY.isoformat()


def parse_month(month_input) -> int:
    if month_input is None:
        return CURRENT_MONTH
    text = str(month_input).strip()
    if text.isdigit():
        m = int(text)
        return m if 1 <= m <= 12 else CURRENT_MONTH
    return MONTH_NAME_TO_NUM.get(text.lower(), CURRENT_MONTH)


def parse_year(year_input) -> int:
    if year_input is None:
        return CURRENT_YEAR
    try:
        y = int(str(year_input).strip())
        return min(y, CURRENT_YEAR)
    except (TypeError, ValueError):
        return CURRENT_YEAR


def parse_day(day_input) -> dt.date:
    if not day_input:
        return _TODAY
    text = str(day_input).strip()[:10]
    try:
        d = dt.date.fromisoformat(text)
        return min(d, _TODAY)
    except ValueError:
        return _TODAY


def _anniversary_on_year(year: int) -> dt.date:
    """Same month/day as today on a given year (handles Feb 29)."""
    try:
        return dt.date(year, _TODAY.month, _TODAY.day)
    except ValueError:
        last_day = calendar.monthrange(year, _TODAY.month)[1]
        return dt.date(year, _TODAY.month, min(_TODAY.day, last_day))


def _exclusive_end(d: dt.date) -> str:
    return (d + dt.timedelta(days=1)).isoformat()


def _month_range(year: int, month: int) -> Tuple[str, str]:
    if year > CURRENT_YEAR or (year == CURRENT_YEAR and month > CURRENT_MONTH):
        raise ValueError("Selected month is in the future.")
    start = dt.date(year, month, 1)
    if month == 12:
        end = dt.date(year + 1, 1, 1)
    else:
        end = dt.date(year, month + 1, 1)
    if end > _TODAY + dt.timedelta(days=1):
        end = _TODAY + dt.timedelta(days=1)
    return start.isoformat(), end.isoformat()


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


def _aggregate_by_period(df: pd.DataFrame, period_col: str) -> Dict[str, List]:
    grouped = df.groupby(period_col, sort=True)
    out = {"Date": [], "Open": [], "High": [], "Low": [], "Close": [], "Volume": []}
    for period, group in grouped:
        out["Date"].append(period.strftime("%Y-%m-%d"))
        out["Open"].append(round(float(group.iloc[0]["Open"]), 2))
        out["High"].append(round(float(group["High"].max()), 2))
        out["Low"].append(round(float(group["Low"].min()), 2))
        out["Close"].append(round(float(group.iloc[-1]["Close"]), 2))
        out["Volume"].append(int(group["Volume"].sum()))
    return out


def _anniversary_year_bucket(d: dt.date) -> int:
    """Year label for the anniversary period containing date d."""
    anchor = _anniversary_on_year(d.year)
    if d < anchor:
        return d.year - 1
    return d.year


def aggregate_to_anniversary_years(data: Dict[str, List], start: dt.date, end: dt.date) -> Dict[str, List]:
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]
    if df.empty:
        return {"Date": [], "Open": [], "High": [], "Low": [], "Close": [], "Volume": []}

    df["Bucket"] = df["Date"].apply(_anniversary_year_bucket)
    grouped = df.groupby("Bucket", sort=True)
    out = {"Date": [], "Open": [], "High": [], "Low": [], "Close": [], "Volume": []}
    for bucket, group in grouped:
        out["Date"].append(_anniversary_on_year(int(bucket)).strftime("%Y-%m-%d"))
        out["Open"].append(round(float(group.iloc[0]["Open"]), 2))
        out["High"].append(round(float(group["High"].max()), 2))
        out["Low"].append(round(float(group["Low"].min()), 2))
        out["Close"].append(round(float(group.iloc[-1]["Close"]), 2))
        out["Volume"].append(int(group["Volume"].sum()))
    return out


def aggregate_to_calendar_months(data: Dict[str, List], start: dt.date, end: dt.date) -> Dict[str, List]:
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    df = df[(df["Date"] >= start) & (df["Date"] <= end)]
    if df.empty:
        return {"Date": [], "Open": [], "High": [], "Low": [], "Close": [], "Volume": []}

    df["Bucket"] = pd.to_datetime(df["Date"]).dt.to_period("M").dt.to_timestamp()
    return _aggregate_by_period(df, "Bucket")


def fetch_stock_data(
    company: str,
    timeframe: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[dt.date] = None,
) -> Tuple[Dict[str, List], str]:
    import yfinance as yf

    ticker_symbol = COMPANY_TICKERS.get(company)
    if not ticker_symbol:
        raise ValueError(f"Unknown company: {company}")

    ticker = yf.Ticker(ticker_symbol)

    if timeframe == "Hourly":
        day = day or _TODAY
        if day > _TODAY:
            raise ValueError("Cannot load hourly data for a future date.")
        start = day.isoformat()
        end = _exclusive_end(day)
        hist = ticker.history(start=start, end=end, interval="1h", auto_adjust=True)
        subtitle = f"{_format_day_label(day)} (hourly)"
        if hist is None or hist.empty:
            raise ValueError(f"No hourly data for {company} on {day.isoformat()}.")
        return _hist_to_ohlcv_dict(hist, include_time=True), subtitle

    if timeframe == "Daily":
        year = parse_year(year) if year else CURRENT_YEAR
        month = parse_month(month) if month else CURRENT_MONTH
        start, end = _month_range(year, month)
        hist = ticker.history(start=start, end=end, interval="1d", auto_adjust=True)
        subtitle = f"{CANDLESTICK_MONTH_LABELS[str(month)]} {year} (trading days)"
        if hist is None or hist.empty:
            raise ValueError(f"No trading data for {company} in {subtitle}.")
        return _hist_to_ohlcv_dict(hist), subtitle

    if timeframe == "Monthly":
        year = parse_year(year) if year else CURRENT_YEAR
        if year > CURRENT_YEAR:
            raise ValueError("Selected year is in the future.")
        period_start = _anniversary_on_year(year - 1)
        period_end = min(_anniversary_on_year(year), _TODAY)
        hist = ticker.history(
            start=period_start.isoformat(),
            end=_exclusive_end(period_end),
            interval="1d",
            auto_adjust=True,
        )
        subtitle = (
            f"{period_start.strftime('%b %d, %Y')} – {period_end.strftime('%b %d, %Y')} (monthly)"
        )
        if hist is None or hist.empty:
            raise ValueError(f"No data for {company} in that monthly range.")
        data = _hist_to_ohlcv_dict(hist)
        data = aggregate_to_calendar_months(data, period_start, period_end)
        if not data["Date"]:
            raise ValueError(f"No monthly bars for {company} in that range.")
        return data, subtitle

    if timeframe == "Yearly":
        period_start = _anniversary_on_year(CURRENT_YEAR - YEARLY_LOOKBACK_YEARS)
        period_end = _TODAY
        hist = ticker.history(
            start=period_start.isoformat(),
            end=_exclusive_end(period_end),
            interval="1d",
            auto_adjust=True,
        )
        subtitle = (
            f"{period_start.strftime('%b %d, %Y')} – {period_end.strftime('%b %d, %Y')} "
            f"({YEARLY_LOOKBACK_YEARS} years)"
        )
        if hist is None or hist.empty:
            raise ValueError(f"No data for {company} over the last {YEARLY_LOOKBACK_YEARS} years.")
        data = _hist_to_ohlcv_dict(hist)
        data = aggregate_to_anniversary_years(data, period_start, period_end)
        return data, subtitle

    raise ValueError(f"Unknown timeframe: {timeframe}")


def generate_stock_data(
    company: str = "Tesla",
    start_date: str = "2023-01-01",
    end_date: str = "2023-12-31",
    seed: Optional[int] = 42,
) -> Dict[str, List]:
    if seed is not None:
        np.random.seed(seed)

    company_params = {
        "Tesla": {"start_price": 200.0, "volatility": 0.025},
        "Apple": {"start_price": 150.0, "volatility": 0.020},
        "Google": {"start_price": 140.0, "volatility": 0.022},
        "Amazon": {"start_price": 120.0, "volatility": 0.024},
    }
    params = company_params.get(company, company_params["Tesla"])
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


def create_candlestick_plot(
    data_dict: Dict[str, List],
    company: str = "Tesla",
    theme: str = "Light",
    timeframe: str = "Daily",
    range_label: str = "",
    data_source: str = "Yahoo Finance",
    **_kwargs,
) -> plt.Axes:
    if not data_dict["Date"]:
        raise ValueError("No data points to plot.")

    df = pd.DataFrame(data_dict)
    df["Date"] = pd.to_datetime(df["Date"])
    ticker = COMPANY_TICKERS.get(company, "")

    title = f"Candlestick: Stock Price {ticker or company}"
    if range_label:
        title += f" — {range_label}"

    if MPLFINANCE_AVAILABLE:
        mpf_df = df.set_index("Date")[["Open", "High", "Low", "Close", "Volume"]]
        if theme == "Dark":
            style = mpf.make_mpf_style(base_mpf_style="nightclouds", rc={"axes.grid": True})
        else:
            style = mpf.make_mpf_style(base_mpf_style="yahoo", rc={"axes.grid": True})

        fig, axes = mpf.plot(
            mpf_df,
            type="candle",
            volume=False,
            returnfig=True,
            style=style,
            title=title,
            ylabel="Price ($)",
            figsize=(12, 6),
            warn_too_much_data=10000,
        )
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
    ax.xaxis_date()
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    return ax


def create_candlestick(
    company: str,
    timeframe: str,
    theme: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[dt.date] = None,
) -> plt.Axes:
    data_source = "Yahoo Finance"
    range_label = ""
    try:
        data, range_label = fetch_stock_data(
            company, timeframe, year=year, month=month, day=day,
        )
    except Exception as e:
        print(f"Live stock fetch failed ({e}); using synthetic fallback.")
        data_source = "Sample data (Yahoo Finance unavailable)"
        y = min(parse_year(year), CURRENT_YEAR) if year else CURRENT_YEAR
        m = parse_month(month) if month else CURRENT_MONTH
        if timeframe == "Hourly":
            d = day or _TODAY
            data = generate_stock_data(company, d.isoformat(), d.isoformat())
            range_label = f"{_format_day_label(d)} (sample)"
        elif timeframe == "Daily":
            start = dt.date(y, m, 1)
            last = min(calendar.monthrange(y, m)[1], _TODAY.day if y == CURRENT_YEAR and m == CURRENT_MONTH else calendar.monthrange(y, m)[1])
            if y == CURRENT_YEAR and m == CURRENT_MONTH:
                last = _TODAY.day
            end = dt.date(y, m, last)
            data = generate_stock_data(company, start.isoformat(), end.isoformat())
            range_label = f"{CANDLESTICK_MONTH_LABELS[str(m)]} {y} (sample)"
        elif timeframe == "Monthly":
            ps = _anniversary_on_year(y - 1)
            pe = min(_anniversary_on_year(y), _TODAY)
            data = generate_stock_data(company, ps.isoformat(), pe.isoformat())
            data = aggregate_to_calendar_months(data, ps, pe)
            range_label = f"{ps} – {pe} (sample)"
        else:
            ps = _anniversary_on_year(CURRENT_YEAR - YEARLY_LOOKBACK_YEARS)
            data = generate_stock_data(company, ps.isoformat(), _TODAY.isoformat())
            data = aggregate_to_anniversary_years(data, ps, _TODAY)
            range_label = f"{ps} – {_TODAY} (sample)"

    return create_candlestick_plot(
        data,
        company=company,
        theme=theme,
        timeframe=timeframe,
        range_label=range_label,
        data_source=data_source,
    )
