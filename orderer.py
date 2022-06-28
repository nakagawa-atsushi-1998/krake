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
        data_range_in_minute=3*60*60,
    ):
        self.pair = pair
        self.time_scale_list = time_scale_list
        self.data_range_in_minute = data_range_in_minute
        self.crypto_list = []
        for counter in range(len(self.time_scale_list)):
            crypto_ = crypto.Crypto(
                pair=self.pair,
                time_scale=self.time_scale_list[counter],
            )
            self.crypto_list = self.crypto_list+[crypto_]
        self.figure, self.axes = plt.subplots(4, 1, figsize=(7.0, 8.0))
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
            start_time = int(time.time()) - self.time_scale_list[counter] * self.data_range_in_minute
            self.collect_data(
                index=counter,
                start_time=start_time
            )

    def collect_data(
        self,
        index,
        start_time,
    ):
        result_list = self.bybit_client.fetch_candle(
            start_time=start_time,
            time_scale=self.time_scale_list[index],
        )
        for counter in range(len(result_list)):
            result = result_list[counter]
            result_reshaped = {
                'Date': datetime.datetime.fromtimestamp(result['open_time']),
                'Open': float(result['open']),
                'High': float(result['high']),
                'Low': float(result['low']),
                'Close': float(result['close']),
                'Volume': int(result['volume']),
            }
            self.crypto_list[index].add_candle(last_row=result_reshaped)
        self.crypto_list[index].calculate_bb()
        self.crypto_list[index].calculate_rsi()
        self.crypto_list[index].calculate_macd()

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
        for cnt in range(len(self.time_scale_list)): #reversedへ変更
            rcnt = len(self.time_scale_list) - cnt - 1
            term = int(self.data_range_in_minute/60/self.time_scale_list[rcnt])
            _datetime = self.crypto_list[rcnt].candle['Date'][-term:]
            _open = self.crypto_list[rcnt].candle['Open'][-term:]
            _close = self.crypto_list[rcnt].candle['Close'][-term:]
            _bbminus = self.crypto_list[rcnt].bb['-2σ'][-term:]
            _bbplus = self.crypto_list[rcnt].bb['+2σ'][-term:]
            _hist = self.crypto_list[rcnt].macd['Hist'][-term:]
            _hrsi = self.crypto_list[rcnt].macd['HistRSI'][-term:]
            _rsi = self.crypto_list[rcnt].rsi['RSI'][-term:]
            self.axes[0].plot(_datetime, _close, color=COLOR.candle[0], alpha=ALPHA[rcnt])
            self.axes[0].plot(_datetime, _open, color=COLOR.candle[1], alpha=ALPHA[rcnt])
            self.axes[0].fill_between(_datetime, _bbminus, _bbplus, facecolor=COLOR.bb[cnt], alpha=ALPHA[rcnt])
            self.axes[1].fill_between(_datetime, _hist, 0, facecolor=COLOR.macd[cnt], alpha=ALPHA[rcnt])
            self.axes[2].plot(_datetime, _rsi, color=COLOR.rsi[cnt], alpha=ALPHA[rcnt])
            self.axes[3].plot(_datetime, _hrsi, color=COLOR.rsi[cnt], alpha=ALPHA[rcnt])
        self.axes[2].fill_between(self.crypto_list[rcnt].candle['Date'], 0, 25, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[2].fill_between(self.crypto_list[rcnt].candle['Date'], 75, 100, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[3].fill_between(self.crypto_list[rcnt].candle['Date'], 0, 25, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[3].fill_between(self.crypto_list[rcnt].candle['Date'], 75, 100, facecolor=COLOR.bb[0], alpha=3/10)
        self.axes[0].grid(alpha=1/4)
        self.axes[1].grid(alpha=1/4)
        self.axes[2].grid(alpha=1/4)
        self.axes[3].grid(alpha=1/4)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def judge_trade(self):
        pass

    def mainloop(self):
        while True:
            now = datetime.datetime.now()
            start_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)
            end_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)+datetime.timedelta(minutes=1)
            while datetime.datetime.now() < end_time:
                plt.pause(5)
            for counter in range(len(self.time_scale_list)):
                self.collect_data(
                    index=counter,
                    start_time=int(end_time.timestamp())
                )
            print(self.crypto_list[0].candle.tail(1))
            self.plot_graph()

def main():
    orderer=Orderer()
    orderer.give_key_to_api(
        KEY.BYBIT_API_ACCESS,
        KEY.BYBIT_API_SECRET,
        KEY.COINCHECK_API_ACCESS,
        KEY.COINCHECK_API_SECRET,
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
