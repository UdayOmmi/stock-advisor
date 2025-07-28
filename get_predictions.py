import yfinance as yf
import pandas as pd
import joblib

stocks = ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS", "LT.NS"]

def get_latest_features(ticker):
    data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False)
    data['Return'] = data['Close'].pct_change()
    data['SMA_5'] = data['Close'].rolling(window=5).mean()
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['Volatility'] = data['Return'].rolling(window=5).std()
    data.dropna(inplace=True)
    row = data.iloc[-1]
    return row[['Close', 'SMA_5', 'SMA_10', 'Volatility']], float(row['Volatility'].item())

def get_risk_label(volatility):
    if volatility <= 0.01:
        return "Low Risk"
    elif volatility <= 0.025:
        return "Moderate Risk"
    else:
        return "High Risk"

def get_stock_scores(days=30):
    stock_scores = {}
    for ticker in stocks:
        try:
            model = joblib.load(f"{ticker.replace('.NS', '')}_model.pkl")
            features, volatility = get_latest_features(ticker)
            risk = get_risk_label(volatility)
            X = features.values.reshape(1, -1)
            confidence = model.predict_proba(X)[0][1]
            stock_scores[ticker] = {
                "confidence": round(confidence, 4),
                "risk": risk
            }
        except Exception as e:
            print(f"Error with {ticker}: {e}")
            continue
    return stock_scores
