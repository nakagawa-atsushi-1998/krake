import json
import time
import datetime
#import tkinter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import configure
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)
from stream import (
    logger,
    #gui
)
from api import (
    coincheck_api,
    line_notify_api
)

class Brain:
    def __init__(
        self,
    ):
        self.cchc=coincheck_api.HttpClient(
            coincheck_api.WebsocketClient())
        self.figure, self.axes=plt.subplots(3, 1, figsize=(7.0, 8.0))
        #self.gui=gui.GUI(tkinter.Tk())
        #self.logger=logger.Logger()

    def give_key_to_api(
        self,
        COINCHECK_API_ACCESS,
        COINCHECK_API_SECRET,
        LINE_API_TOKEN
    ):
        self.cchc.authenticate(
            COINCHECK_API_ACCESS,
            COINCHECK_API_SECRET)
        self.lc=line_notify_api.HttpClient()
        self.lc.authenticate(
            LINE_API_TOKEN)

    def initialize_table(
        self,
    ):
        tran_list=self.cchc.get_transaction()
        tran_df=self.cchc.form_transaction(tran_list)
        balance_=self.cchc.get_balance_until_true()
        balance_dict=self.cchc.account.form_balance(balance_)
        self.cchc.account.balance=self.cchc.account.balance.append(balance_dict, ignore_index=True)
        self.cchc.account.calc_balance(tran_df)
        #self.cchc.account.balance=self.cchc.account.balance.query('JPY > 25000')
        self.cchc.account.balance=self.cchc.account.balance.reset_index(drop=True)
        trade_list=self.cchc.get_trade_list(limit=100)
        trade_df, start_id, end_id = self.cchc.crypto.form_trade_list(trade_list)
        self.cchc.split_trades_into_ohlcv(trade_df); print(self.cchc.crypto.ohlcv.tail(15))
        self.cchc.crypto.init_bb(); print(self.cchc.crypto.bb)
        self.cchc.crypto.init_rsi(); print(self.cchc.crypto.rsi)
        self.cchc.crypto.init_macd(); print(self.cchc.crypto.macd)

    def check_balance(
        self,
        ask_per_rate=0.005,
        bid_per_amount=1,
    ):
        rate_dict=self.cchc.get_rate()
        rate=float(rate_dict['rate'])
        self.order_min=0.005*rate
        self.ask=ask_per_rate*rate
        balance_=self.cchc.get_balance_until_true()
        balance_dict=self.cchc.account.form_balance(balance_)
        self.jpy=float(balance_dict['JPY'])
        self.btc=float(balance_dict['BTC'])
        self.bid=self.btc*bid_per_amount
        if self.jpy >= self.ask:
            self.buy_flg=True
            print('購入可能です.')
        else:
            self.buy_flg=False
            print('残高不足により購入不可です.')
        
        if (self.bid >= 0.005)&(self.btc >= self.bid) :
            self.sell_flg=True
            print('売却可能です.')
        else:
            self.sell_flg=False
            print('残高不足により売却不可です.')
            
    def auto_order(self):
        if self.buy_flg == True:
            while True:
                result=self.cchc.post_market_buy(
                    market_buy_amount=self.ask);print('.', end='')
                if result['success'] == True:
                    break
            print('購入結果:')
            print(result)
            self.check_balance()
        elif self.sell_flg == True:
            while True:
                result=self.cchc.post_market_sell(
                    amount=self.bid);print('.', end='')
                if result['success'] == True:
                    break
            print('売却結果:')
            print(result)
            self.check_balance()
        else:
            result='購入売却残高不足です,'
            print('処理を終了します.')
        send_result=self.lc.send_message(result)
        print('送信結果:')
        print(str(send_result))

    def draw(self):
        while True:
            now=datetime.datetime.now()
            second_=int(now.second/10)*10
            start_time=datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, second_)
            end_time=start_time+datetime.timedelta(seconds=10)
            while datetime.datetime.now() < end_time:
                time.sleep(5)
            self.cchc.heart_beat(beat='③ ')
            self.plot_graph()
            print('plotted.')

    def plot_graph(self):
        path='graph.png'
        self.axes[0].cla()
        self.axes[1].cla()
        self.axes[2].cla()
        self.axes[0].plot(
            self.cchc.crypto.ohlcv['Datetime'],
            self.cchc.crypto.ohlcv['Close'],
            linewidth=1/2,
            color="#808080")
        self.axes[0].fill_between(
            self.cchc.crypto.bb['Datetime'],
            self.cchc.crypto.bb['pBB'],
            self.cchc.crypto.bb['mBB'],
            alpha=0.5,
            facecolor='#606060')
        self.axes[1].fill_between(
            self.cchc.crypto.macd['Datetime'],
            self.cchc.crypto.macd['Signal'],
            alpha=0.5,
            linewidth=1/2,
            color="#404040")
        self.axes[2].plot(
            self.cchc.crypto.rsi['Datetime'],
            self.cchc.crypto.rsi['RSI'],
            alpha=0.5,
            linewidth=1/2,
            color="#202020")
        self.axes[0].grid(alpha=1/4)
        self.axes[1].grid(alpha=1/4)
        self.axes[2].grid(alpha=1/4)
        #self.axes[2].plot(
        #    self.cchc.account.balance['Datetime'],
        #    self.cchc.account.balance['JPY'],
        #    color="#808080",
        #    linewidth=1/2)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.figure.savefig(path)
        plt.show()

    def dominate(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.cchc.connect)
            executor.submit(self.cchc.cast)
            executor.submit(self.draw)
            #executor.submit(self.gui.main)
            #executor.submit(self.logger.logger)

def main():
    brain=Brain()
    brain.give_key_to_api(
        KEY.COINCHECK_API_ACCESS,
        KEY.COINCHECK_API_SECRET,
        KEY.LINE_API_TOKEN)
    trade_dict_list=brain.cchc.get_trade_list(
        limit=100,
        order='desc',
        starting_after=None,
        ending_before=None)
    for trade_dict in trade_dict_list:
        brain.cchc.crypto.trade=brain.cchc.crypto.trade.append(
            trade_dict, ignore_index=True)
    brain.initialize_table()
    brain.dominate()

if __name__ == "__main__":
    KEY=configure.KEY
    PATH=configure.PATH
    COLOR=configure.FORM.Color
    ALPHA=configure.FORM.alpha
    LABEL=configure.FORM.label
    main()


