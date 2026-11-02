# 📈 Stock Market Data Analysis Dashboard

A simple, beginner-friendly stock market analytics dashboard built with **Python**, **Pandas**, **Matplotlib**, and **Streamlit**. 

This project is tailored for academic learning and mini-project submissions. It enables users to explore historical stock prices, analyze trading volumes, calculate daily and monthly investment metrics, and visualize market performance through interactive charts.

---

## 📌 Project Overview & Objectives

* **Objective:** Provide a clear, intuitive visual analytics dashboard for historical stock market data.
* **Beginner-Friendly Architecture:** Organized into modular, clean Python functions without requiring complex frameworks, machine learning, or external database setups.
* **Offline-Ready:** Works immediately out of the box using the included realistic sample dataset (`stock_data.csv`), while also providing flexibility to upload custom CSV files or query live ticker data via `yfinance`.
* **Zero Configuration:** No API keys or paid accounts required.

  
---

## 🚀 Key Features

### 1. Dataset Management
* **Instant Sample Data:** Pre-packaged with `stock_data.csv` containing 90 trading days of realistic price and volume data.
* **Custom CSV Upload:** Upload any stock CSV dataset containing `Date`, `Open`, `High`, `Low`, `Close`, and `Volume`.
* **Optional Live Market Fetching:** Built-in integration with `yfinance` to fetch live historical data for any ticker (e.g., `AAPL`, `MSFT`, `GOOGL`, `TSLA`, `INFY`).
* **Interactive Date Filtering:** Dynamic date range picker that updates all summary statistics and charts instantaneously.
* **Interactive Data Table:** Formatted view of all price figures, volume counts, and percentage returns with a one-click CSV export option.

### 2. Statistical Analysis & Key Performance Indicators (KPIs)
Calculates and displays critical stock metrics:
* **Latest Closing Price:** The most recent closing valuation in the selected period.
* **Highest Stock Price:** Peak price reached within the selected timeframe.
* **Lowest Stock Price:** Lowest intraday price reached within the period.
* **Average Closing Price:** Arithmetic mean of closing prices.
* **Total Trading Volume:** Cumulative volume traded across all selected trading days.
* **Overall Period Return (%):** Net percentage change between the starting and ending close prices.

### 3. Data Visualizations (Matplotlib)
Generates 5 distinct financial charts:
1. **Historical Closing Price Trend (Line Chart):** Visualizes closing price movements over time with subtle gradient shading.
2. **Daily Trading Volume (Bar Chart):** Displays daily volume with green/red color encoding indicating positive or negative daily closing movement.
3. **Open vs. Close Price Comparison (Line Chart):** Compares opening versus closing levels to evaluate intraday price action.
4. **Daily Returns Distribution (Histogram):** Plots the frequency distribution of daily price percentage returns along with the mean return reference line.
5. **Monthly Average Closing Price (Bar Chart):** Aggregates daily closing prices by month with precise price labels on top of each bar.

### 4. Returns & Performance Highlights
* **Daily Percentage Return Formula:**
  $$\text{Daily Return} = \left(\frac{\text{Current Close} - \text{Previous Close}}{\text{Previous Close}}\right) \times 100$$
* **Best-Performing Day:** Highest single-day gain and date.
* **Worst-Performing Day:** Steepest single-day decline and date.
* **Average Daily Return:** Mean daily return percentage.

---

## 🛠️ Technologies Used

* **Python 3.9+**: Core programming language.
* **Pandas**: Data manipulation, cleaning, aggregation, and time series handling.
* **Matplotlib**: Financial charting, histograms, and visualization.
* **Streamlit**: Interactive web dashboard and user interface.
* **yfinance (Optional)**: Fetching historical stock quotes online.

---
