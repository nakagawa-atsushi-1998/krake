import json
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import configure
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)
from api import (
    coincheck_api,
    line_notify_api
)

class Orderer:
    def __init__(
        self,
    ):
        self.cchc=coincheck_api.HttpClient(
            coincheck_api.WebsocketClient())
        self.figure, self.axes=plt.subplots(3, 1, figsize=(7.0, 8.0))

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
                    market_buy_amount=self.ask
                );print('.', end='')
                if result['success'] == True:
                    break
            print('購入結果:')
            print(result)
            self.check_balance()
        elif self.sell_flg == True:
            while True:
                result=self.cchc.post_market_sell(
                    amount=self.bid
                );print('.', end='')
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
        

def main():
    orderer=Orderer()
    orderer.give_key_to_api(
        KEY.COINCHECK_API_ACCESS,
        KEY.COINCHECK_API_SECRET,
        KEY.LINE_API_TOKEN,
    )
    orderer.check_balance(
        ask_per_rate=0.008,
        bid_per_amount=1.0
    )
    orderer.auto_order()

if __name__ == "__main__":
    KEY=configure.KEY
    PATH=configure.PATH
    COLOR=configure.FORM.Color
    ALPHA=configure.FORM.alpha
    LABEL=configure.FORM.label
    main()

