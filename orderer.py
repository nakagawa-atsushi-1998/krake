import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import configure
from model import (
    crypto
)
from external import (
    bybit_api,
    coincheck_api,
    line_notify_api,
)
from stream import (
    logger
)
import warnings
warnings.simplefilter('ignore')

class Orderer:
    def __init__(
        self,
        pair='BTCUSD',
        time_scale_list=[1, 5, 15],
        data_range=3*60*60,
    ):
        self.pair = pair
        self.latest_time = None
        self.latest_price = None # 最新終値
        self.balance_jpy = None # 円残高(価格)
        self.balance_btc = None # 残高量(量)
        self.ask_price = self.ask_amount = None # 買値
        self.bid_price = self.bid_amount = None #　売値
        self.time_scale_list = time_scale_list # 時間足リスト
        self.data_range = data_range # データ範囲
        self.crypto_list = []
        for counter in range(len(self.time_scale_list)):
            crypto_ = crypto.Crypto(
                pair=self.pair,
                time_scale=self.time_scale_list[counter],
            )
            self.crypto_list = self.crypto_list+[crypto_]
        self.figure, self.axes = plt.subplots(5, 1, figsize=(7.0, 8.0))
        plt.ion()

    def give_key_to_api(
        self,
        BYBIT_API_ACCESS,
        BYBIT_API_SECRET,
        COINCHECK_API_ACCESS,
        COINCHECK_API_SECRET,
        LINE_API_TOKEN,
    ):
        self.bybit_client=bybit_api.HttpClient()
        self.bybit_client.authenticate(
            BYBIT_API_ACCESS,
            BYBIT_API_SECRET,
        )
        self.coincheck_client=coincheck_api.HttpClient()
        self.coincheck_client.authenticate(
            COINCHECK_API_ACCESS,
            COINCHECK_API_SECRET,
        )
        self.line_client=line_notify_api.HttpClient()
        self.line_client.authenticate(
            LINE_API_TOKEN,
        )

    def initialize_data(
        self,
    ):
        for counter in range(len(self.time_scale_list)):
            start_time = int(time.time()) - self.time_scale_list[counter] * self.data_range
            self.collect_data(
                index=counter,
                start_time=start_time
            )
        print(self.crypto_list[0].candle.values[-2:])

    def collect_data(
        self,
        index,
        start_time,
    ):  
        result_candle_list = self.bybit_client.fetch_candle(
            start_time=start_time,
            time_scale=self.time_scale_list[index],
        )
        result_balance = self.coincheck_client.get_balance()
        for counter in range(len(result_candle_list)):
            try:
                result_candle = result_candle_list[counter]
                result_candle_reshaped = {
                    'Date': datetime.datetime.fromtimestamp(result_candle['open_time']),
                    'Open': float(result_candle['open']),
                    'High': float(result_candle['high']),
                    'Low': float(result_candle['low']),
                    'Close': float(result_candle['close']),
                    'Volume': int(result_candle['volume']),
                }
                self.crypto_list[index].add_candle(last_row=result_candle_reshaped)
            except:
                print('ローソク足取得失敗')
            try:
                result_pal_reshaped = {
                    'Date': datetime.datetime.fromtimestamp(result_candle['open_time']),
                    'JPY': float(result_balance['jpy']),
                    'BTC': float(result_balance['btc']),
                    'Total': float(result_balance['jpy'])+float(result_balance['btc'])*float(result_candle['close'])*136.7
                }
                self.crypto_list[index].add_pal(last_row=result_pal_reshaped)
            except:
                print('損益取得失敗')
        try:
            self.crypto_list[index].calculate_bb()
            self.crypto_list[index].calculate_rsi()
            self.crypto_list[index].calculate_macd()
            self.latest_time = self.crypto_list[0].candle.at[179, 'Date']
            self.latest_price = self.crypto_list[0].candle.at[179, 'Close']
            self.ask_price = self.balance_jpy = self.crypto_list[0].pal.at[179, 'JPY']
            self.bid_amount = self.balance_btc = self.crypto_list[0].pal.at[179, 'BTC']
        except:
            print('テクニカル指標計算失敗')

    def predict_data(
        self,
    ):
        pass

    def plot_graph(
        self,
    ):
        self.axes[0].clear()
        self.axes[1].clear()
        self.axes[2].clear()
        self.axes[3].clear()
        self.axes[4].clear()
        for cnt in range(len(self.time_scale_list)): #reversedへ変更
            rcnt = len(self.time_scale_list)-1-cnt
            term = int(self.data_range/60/self.time_scale_list[rcnt])
            _datetime = self.crypto_list[rcnt].candle['Date'][-term:]
            _high = self.crypto_list[rcnt].candle['High'][-term:]
            _low = self.crypto_list[rcnt].candle['Low'][-term:]
            _bbminus = self.crypto_list[rcnt].bb['-2σ'][-term:]
            _bbplus = self.crypto_list[rcnt].bb['+2σ'][-term:]
            _hist = self.crypto_list[rcnt].macd['Hist'][-term:]
            _hrsi = self.crypto_list[rcnt].macd['HistRSI'][-term:]
            _rsi = self.crypto_list[rcnt].rsi['RSI'][-term:]
            _profit_and_loss = self.crypto_list[rcnt].pal['Total'][-term:]
            self.axes[0].plot(_datetime, _high, color=COLOR.candle[0], alpha=ALPHA[rcnt])
            self.axes[0].plot(_datetime, _low, color=COLOR.candle[1], alpha=ALPHA[rcnt])
            self.axes[0].fill_between(_datetime, _bbminus, _bbplus, facecolor=COLOR.bb[cnt], alpha=ALPHA[rcnt])
            self.axes[1].fill_between(_datetime, _hist, 0, facecolor=COLOR.macd[cnt], alpha=ALPHA[rcnt])
            self.axes[2].plot(_datetime, _rsi, color=COLOR.rsi[cnt], alpha=ALPHA[rcnt])
            self.axes[3].plot(_datetime, _hrsi, color=COLOR.rsi[cnt], alpha=ALPHA[rcnt])
        self.axes[2].fill_between(self.crypto_list[rcnt].candle['Date'], 0, 25, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[2].fill_between(self.crypto_list[rcnt].candle['Date'], 75, 100, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[3].fill_between(self.crypto_list[rcnt].candle['Date'], 0, 25, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[3].fill_between(self.crypto_list[rcnt].candle['Date'], 75, 100, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[4].plot(_datetime, _profit_and_loss, alpha=ALPHA[rcnt])
        self.axes[0].grid(alpha=1/4)
        self.axes[1].grid(alpha=1/4)
        self.axes[2].grid(alpha=1/4)
        self.axes[3].grid(alpha=1/4)
        self.axes[4].grid(alpha=1/4)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def judge_trade(self):
        pass


    def buy(self):
        result = self.coincheck_client.post_order(
            order_type='market_buy',
            pair='btc_jpy',
            market_buy_amount=self.ask_amount
        )
        self.line_client.send_message(message=result)

    def sell(self):
        result = self.coincheck_client.post_order(
            order_type='market_sell',
            pair='btc_jpy',
            amount=self.bid_price
        )
        self.line_client.send_message(message=result)

    def mainloop(self):
        while True:
            now = datetime.datetime.now()
            last = self.latest_time
            start_time = datetime.datetime(last.year, last.month, last.day, last.hour, last.minute, 0)
            print(start_time)
            end_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)+datetime.timedelta(minutes=1)
            while datetime.datetime.now() < end_time:
                plt.pause(5)
            for counter in range(len(self.time_scale_list)):
                self.collect_data(
                    index=counter,
                    start_time=int(start_time.timestamp())
                )
            print(self.crypto_list[0].candle.values[-2:])
            self.judge_trade()
            self.plot_graph()

def main():
    orderer=Orderer()
    orderer.give_key_to_api(
        KEY.BYBIT_API_ACCESS, KEY.BYBIT_API_SECRET,
        KEY.COINCHECK_API_ACCESS, KEY.COINCHECK_API_SECRET,
        KEY.LINE_API_TOKEN,
    )
    orderer.initialize_data()
    orderer.plot_graph()
    orderer.mainloop()
    
if __name__ == "__main__":
    KEY = configure.KEY
    PATH = configure.PATH
    COLOR = configure.FORM.COLOR
    ALPHA = configure.FORM.alpha
    LABEL = configure.FORM.label
    main()
