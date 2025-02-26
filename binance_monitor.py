import websocket
import json
import requests
import time
from datetime import datetime
import os
import requests
import requests

class BinanceMonitor:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.ws_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_4h"
        self.known_pairs_file = "known_pairs.json"
        self.known_pairs = self.load_known_pairs()

    def get_latest_data(self, symbol):
        try:
            clean_symbol = symbol.replace('.P', '')
            endpoint = f"/fapi/v1/klines"
            url = f"{self.base_url}{endpoint}"
            
            params = {
                'symbol': clean_symbol,
                'interval': '4h',
                'limit': 100
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': clean_symbol,
                    'data': data
                }
            return None
        except Exception as e:
            print(f"Erro ao obter dados para {symbol}: {e}")
            return None

    def load_known_pairs(self):
        if os.path.exists(self.known_pairs_file):
            with open(self.known_pairs_file, 'r') as f:
                return set(json.load(f))
        return set()

    def get_usdt_pairs(self):
        try:
            response = requests.get(self.base_url + "/fapi/v1/exchangeInfo")
            if response.status_code == 200:
                data = response.json()
                return {symbol['symbol'] for symbol in data['symbols'] 
                       if symbol['symbol'].endswith('USDT')}
            else:
                print(f"Error accessing Binance API. Status code: {response.status_code}")
                return set()
        except Exception as e:
            print(f"Error: {e}")
            return set()

    def preview_pairs(self):
        print("Fetching pairs from Binance...")
        current_pairs = self.get_usdt_pairs()
        if current_pairs:
            print("\nCurrent USDT pairs preview:")
            print(f"Total pairs: {len(current_pairs)}")
            print("\nList of all USDT pairs:")
            for pair in sorted(current_pairs):
                print(pair)
            return True
        else:
            print("Failed to fetch pairs from Binance. Please check your internet connection.")
            return False

    def on_message(self, ws, message):
        data = json.loads(message)
        kline = data['k']
        symbol = kline['s']
        open_price = float(kline['o'])
        close_price = float(kline['c'])
        high_price = float(kline['h'])
        low_price = float(kline['l'])
        volume = float(kline['v'])
        is_closed = kline['x']

        if is_closed:
            print(f"Symbol: {symbol}")
            print(f"Open: {open_price}")
            print(f"Close: {close_price}")
            print(f"High: {high_price}")
            print(f"Low: {low_price}")
            print(f"Volume: {volume}")
            print("------------------------")

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def on_open(self, ws):
        print("WebSocket connection opened!")

if __name__ == "__main__":
    monitor = BinanceMonitor()
    
    while True:
        print("\nChoose monitoring mode:")
        print("1. Monitor new listings")
        print("2. Monitor BTC/USDT price")
        print("3. Preview current pairs")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        try:
            if choice == "1":
                monitor.monitor_new_listings(interval=120)
            elif choice == "2":
                monitor.monitor_price()
            elif choice == "3":
                monitor.preview_pairs()
                input("\nPress Enter to return to menu...")
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice!")
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"An error occurred: {e}")