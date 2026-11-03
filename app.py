"""
Stock Market Data Analysis Dashboard
====================================
A beginner-friendly financial analytics web application built with Streamlit,
Pandas, and Matplotlib.

This dashboard allows users to analyze historical stock data, visualize price
and volume trends, compute essential statistical metrics, and evaluate daily returns.
"""

import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import streamlit as st

# Optional import for yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


# -----------------------------------------------------------------------------
# Configuration and Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Market Data Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom light styling for metric cards and headers
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 14px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #212529;
    }
    .sub-note {
        font-size: 0.8rem;
        color: #6c757d;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------------------------------------------------------
# Data Loading & Validation Functions
# -----------------------------------------------------------------------------
REQUIRED_COLUMNS = ["Date", "Open", "High", "Low", "Close", "Volume"]


def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates that the dataframe contains all required columns,
    coerces data types, removes invalid/missing values, and sorts chronologically.
    """
    # Check for missing required columns (case-insensitive check)
    col_mapping = {col.lower(): col for col in df.columns}
    missing_cols = [req for req in REQUIRED_COLUMNS if req.lower() not in col_mapping]

    if missing_cols:
        raise ValueError(f"Uploaded dataset is missing required column(s): {', '.join(missing_cols)}")

    # Standardize column names to Title Case for consistency
    standardized_cols = {col_mapping[req.lower()]: req for req in REQUIRED_COLUMNS}
    df = df.rename(columns=standardized_cols)

    # Keep only the required columns and any extra metadata
    df = df.copy()

    # Parse and validate Date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Coerce numeric columns
    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where essential price/volume data is NaN or non-positive
    df = df.dropna(subset=numeric_cols)
    df = df[(df["Close"] > 0) & (df["Open"] > 0) & (df["High"] > 0) & (df["Low"] > 0)]

    # Sort chronologically and drop duplicate dates
    df = df.sort_values("Date").drop_duplicates(subset=["Date"]).reset_index(drop=True)

    if len(df) == 0:
        raise ValueError("Dataset contains no valid records after cleaning and validation.")

    return df


@st.cache_data
def load_sample_dataset() -> pd.DataFrame:
    """
    Loads the default sample stock_data.csv file included with the project.
    """
    # Look for stock_data.csv in the current script directory or current working directory
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "stock_data.csv"),
        "stock_data.csv",
        "stock-market-analysis/stock_data.csv"
    ]
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if file_path is None:
        raise FileNotFoundError("Default sample dataset 'stock_data.csv' was not found.")

    raw_df = pd.read_csv(file_path)
    return validate_and_clean_data(raw_df)


def load_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """
    Reads an uploaded CSV file from Streamlit and validates it.
    """
    raw_df = pd.read_csv(uploaded_file)
    return validate_and_clean_data(raw_df)


@st.cache_data(show_spinner=False)
def fetch_ticker_data(ticker_symbol: str, start_date, end_date) -> pd.DataFrame:
    """
    Fetches historical stock market data using the yfinance library.
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError("The 'yfinance' library is not installed. Run 'pip install yfinance' to enable live fetching.")

    ticker_obj = yf.Ticker(ticker_symbol.strip().upper())
    # yfinance end_date is exclusive, so add 1 day or use string
    df = ticker_obj.history(start=start_date, end=end_date)

    if df.empty:
        raise ValueError(f"No market data found for ticker '{ticker_symbol}'. Please verify the symbol.")

    df = df.reset_index()

    # Handle datetime timezone if present
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    # Standardize column names
    rename_dict = {}
    for col in df.columns:
        if col.capitalize() in REQUIRED_COLUMNS:
            rename_dict[col] = col.capitalize()
    df = df.rename(columns=rename_dict)

    return validate_and_clean_data(df)


# -----------------------------------------------------------------------------
# Metric Calculations
# -----------------------------------------------------------------------------
def calculate_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes daily percentage returns:
    Daily Return = ((Current Close - Previous Close) / Previous Close) * 100
    Safely handles division by zero or NaN for the first day.
    """
    df = df.copy()
    prev_close = df["Close"].shift(1)
    
    # Avoid zero division
    valid_mask = (prev_close > 0)
    df["Daily_Return"] = 0.0
    df.loc[valid_mask, "Daily_Return"] = (
        (df.loc[valid_mask, "Close"] - prev_close[valid_mask]) / prev_close[valid_mask]
    ) * 100.0
    
    # First row has no previous day
    df.loc[df.index[0], "Daily_Return"] = 0.0
    return df


def compute_summary_statistics(df: pd.DataFrame):
    """
    Calculates overall KPI metrics for the selected time window.
    """
    if df.empty:
        return {}

    first_close = df["Close"].iloc[0]
    latest_close = df["Close"].iloc[-1]
    highest_price = df["High"].max()
    lowest_price = df["Low"].min()
    average_close = df["Close"].mean()
    total_volume = df["Volume"].sum()

    price_diff = latest_close - first_close
    percent_change = (price_diff / first_close * 100.0) if first_close > 0 else 0.0

    # Returns analysis (excluding day 0 where return is undefined/0)
    returns_series = df["Daily_Return"].iloc[1:] if len(df) > 1 else df["Daily_Return"]

    if not returns_series.empty:
        best_day_idx = returns_series.idxmax()
        worst_day_idx = returns_series.idxmin()
        best_day_date = df.loc[best_day_idx, "Date"].strftime("%Y-%m-%d")
        best_day_val = df.loc[best_day_idx, "Daily_Return"]
        worst_day_date = df.loc[worst_day_idx, "Date"].strftime("%Y-%m-%d")
        worst_day_val = df.loc[worst_day_idx, "Daily_Return"]
        avg_daily_return = returns_series.mean()
    else:
        best_day_date, best_day_val = "N/A", 0.0
        worst_day_date, worst_day_val = "N/A", 0.0
        avg_daily_return = 0.0

    return {
        "latest_close": latest_close,
        "highest_price": highest_price,
        "lowest_price": lowest_price,
        "average_close": average_close,
        "total_volume": total_volume,
        "price_diff": price_diff,
        "percent_change": percent_change,
        "best_day_date": best_day_date,
        "best_day_val": best_day_val,
        "worst_day_date": worst_day_date,
        "worst_day_val": worst_day_val,
        "avg_daily_return": avg_daily_return,
    }


# -----------------------------------------------------------------------------
# Matplotlib Visualization Helpers
# -----------------------------------------------------------------------------
def plot_closing_price_trend(df: pd.DataFrame):
    """1. Line Chart: Historical Closing Prices over time."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df["Date"], df["Close"], color="#1f77b4", linewidth=2.0, label="Closing Price")
    ax.fill_between(df["Date"], df["Close"], color="#1f77b4", alpha=0.1)

    ax.set_title("Historical Closing Price Over Time", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Price ($)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    return fig


def plot_daily_trading_volume(df: pd.DataFrame):
    """2. Bar Chart: Daily Trading Volume."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    
    # Color volume green if close >= open, else red
    colors = ["#2ca02c" if c >= o else "#d62728" for c, o in zip(df["Close"], df["Open"])]
    ax.bar(df["Date"], df["Volume"] / 1e6, color=colors, alpha=0.85, width=0.8)

    ax.set_title("Daily Trading Volume (in Millions)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Volume (Millions)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    return fig


def plot_open_vs_close(df: pd.DataFrame):
    """3. Line Chart: Comparison of Opening vs. Closing Prices."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df["Date"], df["Open"], color="#ff7f0e", linestyle="--", linewidth=1.8, label="Open Price")
    ax.plot(df["Date"], df["Close"], color="#2ca02c", linewidth=2.0, label="Close Price")

    ax.set_title("Opening vs. Closing Prices", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Price ($)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d, %Y"))
    fig.autofmt_xdate(rotation=30)
    ax.legend(loc="upper left", frameon=True)
    plt.tight_layout()
    return fig


def plot_daily_returns_distribution(df: pd.DataFrame):
    """4. Histogram: Distribution of Daily Stock Returns."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    returns_series = df["Daily_Return"].iloc[1:] if len(df) > 1 else df["Daily_Return"]
    
    counts, bins, patches = ax.hist(
        returns_series,
        bins=25,
        color="#3b528b",
        edgecolor="white",
        alpha=0.85
    )

    mean_ret = returns_series.mean()
    ax.axvline(mean_ret, color="#d62728", linestyle="--", linewidth=1.8, label=f"Mean Return: {mean_ret:.2f}%")
    ax.axvline(0, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)

    ax.set_title("Distribution of Daily Returns (%)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Daily Return (%)", fontsize=10)
    ax.set_ylabel("Frequency (Trading Days)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    return fig


def plot_monthly_average_close(df: pd.DataFrame):
    """5. Bar Chart: Monthly Average Closing Prices."""
    fig, ax = plt.subplots(figsize=(10, 4.2))
    df_copy = df.copy()
    df_copy["YearMonth"] = df_copy["Date"].dt.to_period("M").astype(str)
    monthly_avg = df_copy.groupby("YearMonth")["Close"].mean().reset_index()

    bars = ax.bar(monthly_avg["YearMonth"], monthly_avg["Close"], color="#4c72b0", width=0.5, edgecolor="black", alpha=0.85)

    # Annotate value on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"${height:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold"
        )

    ax.set_title("Monthly Average Closing Price", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Month", fontsize=10)
    ax.set_ylabel("Average Close Price ($)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    
    # Set y-limits with padding so annotations fit comfortably
    if not monthly_avg.empty:
        min_val = monthly_avg["Close"].min()
        max_val = monthly_avg["Close"].max()
        ax.set_ylim(max(0, min_val * 0.85), max_val * 1.12)

    plt.tight_layout()
    return fig


# -----------------------------------------------------------------------------
# Main Application Layout
# -----------------------------------------------------------------------------
def main():
    # Header Section
    st.title("📈 Stock Market Data Analysis")
    st.caption("A beginner-friendly historical price & volume analytics dashboard built with Python, Pandas, and Matplotlib.")

    # Sidebar - Data Source Selection
    st.sidebar.header("📁 Data Management")
    data_source = st.sidebar.radio(
        "Choose Data Source:",
        options=["Sample Dataset (Included)", "Upload Custom CSV", "Fetch Online (Yahoo Finance)"],
        index=0
    )

    df_raw = None
    is_sample_data = False
    source_label = ""

    # Handling Data Sources
    try:
        if data_source == "Sample Dataset (Included)":
            df_raw = load_sample_dataset()
            is_sample_data = True
            source_label = "Sample Dataset (stock_data.csv)"
            st.sidebar.success("Loaded pre-packaged sample dataset.")

        elif data_source == "Upload Custom CSV":
            uploaded_file = st.sidebar.file_uploader(
                "Upload Stock CSV File",
                type=["csv"],
                help="CSV must contain: Date, Open, High, Low, Close, Volume"
            )
            if uploaded_file is not None:
                df_raw = load_uploaded_csv(uploaded_file)
                source_label = f"Uploaded File: {uploaded_file.name}"
                st.sidebar.success("CSV uploaded and validated successfully!")
            else:
                st.sidebar.info("Please upload a CSV file with columns: Date, Open, High, Low, Close, Volume.")
                st.info("👈 Please upload a CSV file from the sidebar, or select 'Sample Dataset' to explore immediately.")
                return

        elif data_source == "Fetch Online (Yahoo Finance)":
            if not YFINANCE_AVAILABLE:
                st.sidebar.error("yfinance package is not installed. Please run: pip install yfinance")
                return

            ticker_input = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL").strip().upper()
            default_start = datetime(2023, 1, 1).date()
            default_end = datetime.now().date()
            
            fetch_btn = st.sidebar.button("Fetch Market Data", use_container_width=True)
            
            # Use session state to cache fetched online data
            if "fetched_ticker_df" not in st.session_state or fetch_btn:
                if ticker_input:
                    with st.spinner(f"Fetching historical data for {ticker_input}..."):
                        try:
                            df_fetched = fetch_ticker_data(ticker_input, default_start, default_end)
                            st.session_state["fetched_ticker_df"] = df_fetched
                            st.session_state["fetched_ticker_name"] = ticker_input
                        except Exception as e:
                            st.sidebar.error(f"Error fetching data: {str(e)}")
                            return
                else:
                    st.sidebar.warning("Please enter a valid ticker symbol.")
                    return

            if "fetched_ticker_df" in st.session_state:
                df_raw = st.session_state["fetched_ticker_df"]
                source_label = f"Yahoo Finance ({st.session_state.get('fetched_ticker_name', ticker_input)})"

    except Exception as err:
        st.error(f"Failed to load dataset: {str(err)}")
        return

    if df_raw is None or df_raw.empty:
        st.warning("No data available to display.")
        return

    # Add Daily Return Column to raw dataset
    df_with_returns = calculate_daily_returns(df_raw)

    # Sidebar - Date Range Filter
    st.sidebar.markdown("---")
    st.sidebar.header("📅 Date Filter")
    min_date = df_with_returns["Date"].min().date()
    max_date = df_with_returns["Date"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter the analysis and charts to a specific timeframe."
    )

    # Validate selected date range tuple
    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_filter, end_filter = selected_date_range
    elif isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 1:
        start_filter = selected_date_range[0]
        end_filter = max_date
    else:
        start_filter, end_filter = min_date, max_date

    # Filter data according to user selection
    mask = (df_with_returns["Date"].dt.date >= start_filter) & (df_with_returns["Date"].dt.date <= end_filter)
    filtered_df = df_with_returns.loc[mask].reset_index(drop=True)

    if filtered_df.empty:
        st.warning("No records found in the selected date range. Please widen your date selection.")
        return

    # Recalculate daily returns on filtered slice so day 1 of the selected window has 0% return
    filtered_df = calculate_daily_returns(filtered_df)

    # Compute Key Performance Statistics
    stats = compute_summary_statistics(filtered_df)

    # Notice banner for sample or online data
    if is_sample_data:
        st.info("ℹ️ **Sample Data Mode:** You are viewing synthetic, illustrative stock data. This is not actual historical market data.")
    else:
        st.info(f"📊 **Data Active:** {source_label} | Filtered Window: {start_filter.strftime('%b %d, %Y')} to {end_filter.strftime('%b %d, %Y')}")

    # -------------------------------------------------------------------------
    # Section 1: KPI Summary Cards
    # -------------------------------------------------------------------------
    st.markdown("### 📌 Key Performance Indicators (KPIs)")
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    with kpi1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Latest Close</div>
                <div class="metric-value">${stats['latest_close']:.2f}</div>
                <div class="sub-note">Most recent price</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Highest Price</div>
                <div class="metric-value">${stats['highest_price']:.2f}</div>
                <div class="sub-note">Period high</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Lowest Price</div>
                <div class="metric-value">${stats['lowest_price']:.2f}</div>
                <div class="sub-note">Period low</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Close</div>
                <div class="metric-value">${stats['average_close']:.2f}</div>
                <div class="sub-note">Mean closing price</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi5:
        volume_in_m = stats['total_volume'] / 1e6
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Volume</div>
                <div class="metric-value">{volume_in_m:,.1f}M</div>
                <div class="sub-note">{stats['total_volume']:,} shares</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with kpi6:
        pct = stats['percent_change']
        color = "#2ca02c" if pct >= 0 else "#d62728"
        arrow = "▲" if pct >= 0 else "▼"
        st.markdown(
            f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-label">Period Return</div>
                <div class="metric-value" style="color: {color};">{arrow} {pct:+.2f}%</div>
                <div class="sub-note">Price change (${stats['price_diff']:+.2f})</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Section 2: Visualizations
    # -------------------------------------------------------------------------
    st.markdown("### 📊 Stock Price & Volume Charts")

    # Chart 1: Historical Closing Prices
    st.subheader("1. Historical Closing Price Trend")
    st.pyplot(plot_closing_price_trend(filtered_df))

    col_chart_left, col_chart_right = st.columns(2)

    with col_chart_left:
        # Chart 2: Daily Trading Volume
        st.subheader("2. Daily Trading Volume")
        st.pyplot(plot_daily_trading_volume(filtered_df))

    with col_chart_right:
        # Chart 3: Open vs. Close Comparison
        st.subheader("3. Opening vs. Closing Prices")
        st.pyplot(plot_open_vs_close(filtered_df))

    col_chart_ret, col_chart_month = st.columns(2)

    with col_chart_ret:
        # Chart 4: Daily Returns Histogram
        st.subheader("4. Daily Returns Distribution")
        st.pyplot(plot_daily_returns_distribution(filtered_df))

    with col_chart_month:
        # Chart 5: Monthly Average Closing Price
        st.subheader("5. Monthly Average Closing Price")
        st.pyplot(plot_monthly_average_close(filtered_df))

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Section 3: Detailed Return & Performance Analysis
    # -------------------------------------------------------------------------
    st.markdown("### 🎯 Daily Returns & Performance Highlights")

    ret1, ret2, ret3, ret4 = st.columns(4)
    with ret1:
        st.metric(
            label="🏆 Best-Performing Day",
            value=f"{stats['best_day_val']:+.2f}%",
            delta=f"Date: {stats['best_day_date']}",
            delta_color="normal"
        )
    with ret2:
        st.metric(
            label="⚠️ Worst-Performing Day",
            value=f"{stats['worst_day_val']:+.2f}%",
            delta=f"Date: {stats['worst_day_date']}",
            delta_color="inverse"
        )
    with ret3:
        st.metric(
            label="📊 Average Daily Return",
            value=f"{stats['avg_daily_return']:+.2f}%",
            delta="Mean per day"
        )
    with ret4:
        st.metric(
            label="📈 Total Period Change",
            value=f"{stats['percent_change']:+.2f}%",
            delta=f"${stats['price_diff']:+.2f}"
        )

    st.markdown("---")

    # -------------------------------------------------------------------------
    # Section 4: Tabular Data View & Export
    # -------------------------------------------------------------------------
    st.markdown("### 📋 Historical Data Table")
    
    # Format table for clean display
    display_df = filtered_df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    
    # Reorder columns
    cols_to_show = ["Date", "Open", "High", "Low", "Close", "Volume", "Daily_Return"]
    display_df = display_df[cols_to_show]

    st.dataframe(
        display_df.style.format({
            "Open": "${:.2f}",
            "High": "${:.2f}",
            "Low": "${:.2f}",
            "Close": "${:.2f}",
            "Volume": "{:,.0f}",
            "Daily_Return": "{:+.2f}%"
        }),
        use_container_width=True,
        height=300
    )

    # Download CSV button
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_stock_data.csv",
        mime="text/csv"
    )

    # Disclaimer Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #6c757d; text-align: center;">
            ⚠️ <b>Educational Disclaimer:</b> This dashboard is developed strictly for academic, educational,
            and mini-project presentation purposes. It does not provide financial or investment recommendations.
            Any synthetic or sample data shown is for illustrative purposes only.
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
