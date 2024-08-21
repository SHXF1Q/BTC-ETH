from flask import Flask, send_from_directory
import os
import json
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime as dt
import time
import logging
import threading
from cryptodata import fetch_and_save_data

app = Flask(__name__)

# Background thread to fetch and save data
def background_fetch_and_save_data():
    while True:
        fetch_and_save_data()
        time.sleep(5)

# Serve the JSON file
@app.route('/crypto_data.json')
def serve_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(current_dir, 'crypto_data.json')

# Function to get top 3 cryptocurrencies
def get_top_3_cryptos():
   
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'crypto_data.json')
    print(current_dir)
    print(file_path)

    for attempt in range(3):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return [coin['symbol'].upper() + '-USD' for coin in data['data'][:3]]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Attempt {attempt + 1}: Error reading JSON file: {e}")
            time.sleep(5)
    
    return []

# Function to get 

def get_data(symbols):
    start_date = '2022-01-01'
    end_date = dt.now().strftime('%Y-%m-%d')

    logging.info(f"Start Date: {start_date}")
    logging.info(f"End Date: {end_date}")

    data = {}
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date)
            if not df.empty:
                data[symbol] = df
            else:
                logging.warning(f"No data found for {symbol}")
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {e}")
    return data

@app.route('/')
def index():
    top_3_cryptos = get_top_3_cryptos()
    if not top_3_cryptos:
        logging.error("Failed to fetch top 3 cryptocurrencies.")
        return "Failed to fetch top 3 cryptocurrencies."

    logging.info(f"Top 3 Cryptocurrencies: {top_3_cryptos}")

    crypto_data = get_data(top_3_cryptos)
    if not crypto_data:
        logging.error("Failed to fetch cryptocurrency data.")
        return "Failed to fetch cryptocurrency data."

    fig = make_subplots(
        rows=3, 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.10,
        subplot_titles=top_3_cryptos
    )

    for i, symbol in enumerate(top_3_cryptos):
        if symbol not in crypto_data:
            continue
        df = crypto_data[symbol]

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'].rolling(window=20).mean(),
            mode='lines',
            name=f'{symbol} 20-Day MA',
            line=dict(color='orange', width=1.3)
        ), row=i+1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'].rolling(window=30).mean(),
            mode='lines',
            name=f'{symbol} 30-Day MA',
            line=dict(color='blue', width=1.3)
        ), row=i+1, col=1)

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            increasing_line_color='lime',
            decreasing_line_color='red',
            name=symbol
        ), row=i+1, col=1)

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        autosize=True, 
        height=800, 
        width=1200, 
        xaxis=dict(showline=True, linewidth=2, linecolor='white'),
        yaxis=dict(showline=True, linewidth=2, linecolor='white')
    )

    for i in range(1, 4):
        fig.update_xaxes(
            showline=True, 
            linewidth=2, 
            linecolor='white', 
            row=i, 
            col=1
        )
        fig.update_yaxes(
            showline=True, 
            linewidth=2, 
            linecolor='white', 
            row=i, 
            col=1
        )
        fig.update_xaxes(rangeslider_visible=False, row=i, col=1)

    graph_html = fig.to_html(full_html=False)

    with open("index.html", "r") as f:
        html_content = f.read()
    return html_content.replace("{{ graph_html|safe }}", graph_html)
    

if __name__ == '__main__':
    threading.Thread(target=background_fetch_and_save_data, daemon=True).start()
    app.run(debug=True)