from get_predictions import get_stock_scores
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import traceback

def get_monthly_returns(ticker):
    data = yf.download(ticker, period="2y", interval="1d", auto_adjust=False)
    if data.empty:
        return None
    today = data.index[-1]
    price_now = float(data['Close'].iloc[-1])
    
    def get_price_at_months_ago(months):
        target_date = today - pd.DateOffset(months=months)
        past_data = data[data.index <= target_date]
        if past_data.empty:
            return None
        return float(past_data['Close'].iloc[-1])
    
    periods = [2, 6, 12, 24]
    returns = {}
    for m in periods:
        past_price = get_price_at_months_ago(m)
        if past_price is not None:
            gain = ((price_now - past_price) / past_price) * 100
            returns[f"{m} Months"] = round(gain, 2)
        else:
            returns[f"{m} Months"] = None
    return returns

def plot_returns(ticker, returns):
    labels = list(returns.keys())
    values = []
    for k in labels:
        v = returns[k]
        try:
            if v is None:
                values.append(0)
            elif isinstance(v, pd.Series):
                values.append(float(v.iloc[0]))
            else:
                values.append(float(v))
        except:
            values.append(0)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)
    plt.title(f"{ticker} - Projected Profit Over Time")
    plt.xlabel("Holding Period")
    plt.ylabel("Gain (%)")
    plt.grid(axis='y')
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value}%", ha='center', va='bottom')
    plt.tight_layout()
    plt.show()

def suggest_holding_period(capital):
    if capital < 10000:
        return 15
    elif capital < 50000:
        return 30
    else:
        return 90

def advise_portfolio(capital, diversify=True):
    days = suggest_holding_period(capital)
    print(f"\nSuggested holding period: {days} days\n")
    scores = get_stock_scores(days=days)
    if not scores:
        print("No stock predictions available.")
        return
    if diversify:
        print(f"Suggested diversified investment for ₹{capital}:\n")
        top_stocks = dict(sorted(scores.items(), key=lambda x: x[1]['confidence'], reverse=True)[:3])
        total_score = sum(stock['confidence'] for stock in top_stocks.values())
        for stock, info in top_stocks.items():
            amount = round((info['confidence'] / total_score) * capital, 2)
            print(f"{stock}: ₹{amount} | Confidence: {info['confidence']*100:.2f}% | Risk: {info['risk']}")
            returns = get_monthly_returns(stock)
            if returns:
                plot_returns(stock, returns)
    else:
        top_stock = max(scores.items(), key=lambda x: x[1]['confidence'])
        ticker, info = top_stock
        print(f"Best single stock suggestion:")
        print(f"Invest ₹{capital} in {ticker} | Confidence: {info['confidence']*100:.2f}% | Risk: {info['risk']}")
        returns = get_monthly_returns(ticker)
        if returns:
            plot_returns(ticker, returns)

if __name__ == "__main__":
    try:
        capital = float(input("Enter how much money you want to invest: "))
        choice = input("Do you want to diversify? (yes/no): ").strip().lower()
        diversify = choice == "yes"
        advise_portfolio(capital, diversify)
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
