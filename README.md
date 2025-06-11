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
📦 investing-insights/
├── app.py # Flask app with routes
├── main3.py # Data fetching & PostgreSQL ETL
├── static/
│ ├── css/style.css
│ └── js/main.js
├── templates/
│ └── index.html
├── cleaned_tickers.csv # Input tickers with asset types
└── requirements.txt



## ▶️ Running the App
1. Fetch Data
bash
Kopieren
Bearbeiten
python main3.py

2. Launch Flask Server
bash
Kopieren
Bearbeiten
python app.py
Navigate to http://localhost:5000 in your browser.



## 🌐 Deployment

- Backend hosted on AWS EC2
- Database managed via AWS RDS (PostgreSQL)
