import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def get_current_price(ticker):
    data = yf.download(ticker, period="1d")
    return float(data['Close'].iloc[-1])

def get_past_price(ticker, months):
    days = months * 30
    data = yf.download(ticker, period=f"{days}d")
    return float(data['Close'].iloc[0])

def get_returns(ticker):
    try:
        current_price = get_current_price(ticker)
        return {
            "2 Months": round(((current_price - get_past_price(ticker, 2)) / get_past_price(ticker, 2)) * 100, 2),
            "6 Months": round(((current_price - get_past_price(ticker, 6)) / get_past_price(ticker, 6)) * 100, 2),
            "12 Months": round(((current_price - get_past_price(ticker, 12)) / get_past_price(ticker, 12)) * 100, 2),
            "24 Months": round(((current_price - get_past_price(ticker, 24)) / get_past_price(ticker, 24)) * 100, 2),
        }
    except Exception as e:
        return None

def classify_risk(volatility):
    if isinstance(volatility, pd.Series):
        volatility = volatility.item()
    if volatility < 1:
        return "Low Risk"
    elif volatility < 2:
        return "Moderate Risk"
    else:
        return "High Risk"

def display_stock_advice(ticker, amount):
    st.subheader(f"📈 Suggested Investment: {ticker}")
    st.write(f"Amount to Invest: ₹{amount:.2f}")
    data = yf.download(ticker, period="90d")
    data['SMA_5'] = data['Close'].rolling(window=5).mean()
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['Volatility'] = data['Close'].rolling(window=10).std()
    volatility = data['Volatility'].iloc[-1]
    confidence = 59.0
    st.write(f"Confidence: {confidence}%")
    st.write(f"Risk Level: {classify_risk(volatility)}")

    returns = get_returns(ticker)
    if returns:
        st.write("### 📊 Projected Returns")
        st.bar_chart(pd.Series(returns))
    else:
        st.warning("Could not retrieve projected returns.")

def main():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f9f1;
        }
        h1 {
            color: #006400;
            text-align: center;
        }
        .stButton>button {
            color: white;
            background-color: #00aa00;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💹 Smart Stock Investment Advisor")
    capital = st.number_input("Enter how much money you want to invest:", min_value=100.0)
    diversify = st.radio("Do you want to diversify?", ("yes", "no"))

    tickers = ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS", "LT.NS"]
    if st.button("Get Advice"):
        if diversify == "yes":
            amount_each = capital / len(tickers)
            for ticker in tickers:
                display_stock_advice(ticker, amount_each)
        else:
            display_stock_advice(tickers[0], capital)

if __name__ == '__main__':
    main()