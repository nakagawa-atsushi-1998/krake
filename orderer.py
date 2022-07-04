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
        self.time_scale_list = time_scale_list # 時間足リスト
        self.data_range = data_range # データ範囲
        self.crypto_list = []
        for counter in range(len(self.time_scale_list)):
            crypto_ = crypto.Crypto(
                time_scale=self.time_scale_list[counter],
            )
            self.crypto_list = self.crypto_list+[crypto_]
        self.figure, self.axes = plt.subplots(3, 1, figsize=(7.0, 8.0))
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

    def collect_data(
        self,
        index,
        start_time,
    ):
        result_candle_list = self.bybit_client.fetch_candle(
            start_time=start_time,
            time_scale=self.time_scale_list[index],
        )
        #result_balance = self.coincheck_client.get_balance()
        for counter in range(len(result_candle_list)):
            result_candle = result_candle_list[counter]
            result_candle_reshaped = {
                'Datetime': datetime.datetime.fromtimestamp(result_candle['open_time']),
                'Open': float(result_candle['open']),
                'High': float(result_candle['high']),
                'Low': float(result_candle['low']),
                'Close': float(result_candle['close']),
                'Volume': int(result_candle['volume']),
            }
            self.crypto_list[index].add_ohlcv(ohlcv_dict=result_candle_reshaped)
            self.crypto_list[index].calculate_bb()
            self.crypto_list[index].calculate_ps()
            self.crypto_list[index].calculate_rsi()
            self.crypto_list[index].calculate_macd()

    def plot_graph(
        self,
    ):
        [self.axes[counter].clear() for counter in range(0, 2)]
        for cnt in range(len(self.time_scale_list)): #reversedへ変更
            rcnt = len(self.time_scale_list)-1-cnt
            term = int(self.data_range/60/self.time_scale_list[rcnt])
            _datetime = self.crypto_list[rcnt].ohlcv['Datetime'][-term:]
            _high = self.crypto_list[rcnt].ohlcv['High'][-term:]
            _low = self.crypto_list[rcnt].ohlcv['Low'][-term:]
            _bbminus = self.crypto_list[rcnt].bb['mBB'][-term:]
            _bbplus = self.crypto_list[rcnt].bb['pBB'][-term:]
            _ps = self.crypto_list[rcnt].ps['SAR'][-term:]
            _hist = self.crypto_list[rcnt].macd['Hist'][-term:]
            _rsi = self.crypto_list[rcnt].rsi['RSI'][-term:]
            self.axes[0].plot(_datetime, _high, color=COLOR.candle[0], alpha=ALPHA[rcnt])
            self.axes[0].plot(_datetime, _low, color=COLOR.candle[1], alpha=ALPHA[rcnt])
            self.axes[0].scatter(_datetime, _ps, c=COLOR.ps[cnt], s=1/2, alpha=ALPHA[rcnt])
            self.axes[0].fill_between(_datetime, _bbminus, _bbplus, facecolor=COLOR.bb[cnt], alpha=ALPHA[rcnt])
            #self.axes[1].fill_between(_datetime, _hist, 0, facecolor=COLOR.macd[cnt], alpha=ALPHA[rcnt])
            #self.axes[2].plot(_datetime, _rsi, color=COLOR.rsi[cnt], alpha=ALPHA[rcnt])
        #self.axes[2].fill_between(self.crypto_list[rcnt].ohlcv['Datetime'], 0, 25, facecolor=COLOR.bb[0], alpha=3/10)
        #self.axes[2].fill_between(self.crypto_list[rcnt].ohlcv['Datetime'], 75, 100, facecolor=COLOR.bb[0], alpha=3/10)
        [self.axes[counter].grid(alpha=1/4) for counter in range(0, 2)]
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

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

    def initialize_data(
        self,
    ):
        for i in range(len(self.time_scale_list)):
            start_time = int(time.time())-self.time_scale_list[i]*self.data_range
            result_ohlcv_list = self.bybit_client.fetch_candle(
                start_time=start_time,
                time_scale=self.time_scale_list[i],
            )
            for j in range(len(result_ohlcv_list)):
                result_ohlcv = result_ohlcv_list[j]
                ohlcv_dict = {
                    'Datetime': datetime.datetime.fromtimestamp(result_ohlcv['open_time']),
                    'Open': float(result_ohlcv['open']),
                    'High': float(result_ohlcv['high']),
                    'Low': float(result_ohlcv['low']),
                    'Close': float(result_ohlcv['close']),
                    'Volume': int(result_ohlcv['volume']),
                }
                self.crypto_list[i].add_ohlcv(ohlcv_dict=ohlcv_dict)
            self.crypto_list[i].initialize_bb()
            self.crypto_list[i].initialize_ps()
            self.crypto_list[i].initialize_rsi()
            self.crypto_list[i].initialize_macd()

    def mainloop(self):
        while True:
            now = datetime.datetime.now()
            start_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)-datetime.timedelta(minutes=1)
            end_time = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, 0)+datetime.timedelta(minutes=1)
            while datetime.datetime.now() < end_time:
                plt.pause(3)
            for counter in range(len(self.time_scale_list)):
                self.collect_data(
                    index=counter,
                    start_time=int(start_time.timestamp())
                )
            print(self.crypto_list[0].candle.values[-2:])
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
