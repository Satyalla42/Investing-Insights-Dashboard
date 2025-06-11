# 💸 Investing Insights

A full-stack Flask application that collects, stores, and visualizes financial data for stocks, ETFs, and cryptocurrencies — built to empower data-driven investment decisions.

![image](https://github.com/user-attachments/assets/6e254268-6878-4e7a-b372-5fd006dddf79)



---

## 🚀 Project Overview

**Investing Insights** fetches financial time series from the `yfinance` API, stores it in an AWS RDS PostgreSQL database, and serves it through a Flask-powered HTML dashboard hosted on an EC2 instance. The app includes dynamic charts powered by Chart.js and key performance indicators (KPIs) for investment analysis.

---

## 📊 Features

- Fetch historical price data for **Stocks**, **ETFs**, and **Crypto**
- Store clean data in **PostgreSQL (AWS RDS)**
- View time series with **interactive candlestick and volume charts**
- Calculate KPIs like:
  - Latest price
  - Daily return
  - 30-day volatility
  - High/Low price
  - Average volume
- Download filtered data as CSV

---

## 🧩 Tech Stack

| Layer            | Tool / Tech                         |
|------------------|-------------------------------------|
| Data Source      | [yfinance](https://pypi.org/project/yfinance/) |
| Backend          | Python, Flask                       |
| Frontend         | HTML, CSS, Bootstrap, Chart.js      |
| Database         | PostgreSQL (AWS RDS)                |
| Hosting          | AWS EC2                             |

---

## 📂 Project Structure

