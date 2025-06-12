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
<img width="525" alt="image" src="https://github.com/user-attachments/assets/d28b7a2b-7c5d-4295-abd2-98b8479bc846" />




## ▶️ Running the App
1. Fetch Data
- python3 main3.py

2. Launch Flask Server
- python3 app.py

3. Navigate to http://localhost:5000 in your browser.



## 🌐 Deployment

- Backend hosted on AWS EC2
- Database managed via AWS RDS (PostgreSQL)

![image](https://github.com/user-attachments/assets/4b8affad-bb98-401d-8c1e-c0a1b77818b4)

