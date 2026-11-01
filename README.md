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
