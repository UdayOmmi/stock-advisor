import yfinance as yf
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

stocks = ["TCS.NS", "INFY.NS", "HDFCBANK.NS", "RELIANCE.NS", "LT.NS"]

def train_model(ticker):
    data = yf.download(ticker, start="2020-01-01", end="2024-12-31", auto_adjust=False)
    data['Return'] = data['Close'].pct_change()
    data['SMA_5'] = data['Close'].rolling(window=5).mean()
    data['SMA_10'] = data['Close'].rolling(window=10).mean()
    data['Volatility'] = data['Return'].rolling(window=5).std()
    data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
    data.dropna(inplace=True)
    X = data[['Close', 'SMA_5', 'SMA_10', 'Volatility']]
    y = data['Target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{ticker} Accuracy: {accuracy * 100:.2f}%")
    joblib.dump(model, f"{ticker.replace('.NS', '')}_model.pkl")

for stock in stocks:
    train_model(stock)
