import time
import datetime
import tkinter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)
from stream import (
    logger,
    gui
)
from api import (
    coincheck_api,
    line_notify_api
)
import configure

class Core:
    def __init__(
        self,
    ):
        self.gui=gui.GUI(tkinter.Tk())
        self.orderer=Orderer()

    def give_key_to_api(
        self,
        COINCHECK_API_ACCESS,
        COINCHECK_API_SECRET,
        LINE_API_TOKEN
    ):
        self.ccwc=coincheck_api.WebsocketClient()
        self.cchc=coincheck_api.HttpClient()
        self.cchc.authenticate(
            COINCHECK_API_ACCESS,
            COINCHECK_API_SECRET)
        self.lc=line_notify_api.HttpClient()
        self.lc.authenticate(
            LINE_API_TOKEN)

    def initialize_table(
        self,
    ):
        trades=self.cchc.get_trades(
            limit=100,
        )
        trade_df, start_id, end_id=self.cchc.form_trades(trades)
        print(trade_df); print(start_id, end_id)
        self.cchc.split_trades_into_ohlcv(trade_df)

    def main(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.ccwc.connect)
            executor.submit(self.ccwc.collect)
            executor.submit(self.gui.main)

def main():
    core=Core()
    core.give_key_to_api(
        KEY.COINCHECK_API_ACCESS,
        KEY.COINCHECK_API_SECRET,
        KEY.LINE_API_TOKEN,
    )
    core.initialize_table()
    core.main()

if __name__ == "__main__":
    KEY = configure.KEY
    PATH = configure.PATH
    COLOR = configure.FORM.COLOR
    ALPHA = configure.FORM.alpha
    LABEL = configure.FORM.label
    main()



class Orderer:
    def __init__(self):
        self.basic_price:float #基準値
        self.tolerance_pct:float #許容誤差比率
        self.upper_tolerance:float #許容上限値
        self.lower_tolerance:float #許容下限値
    
    def mainloop(self):    #スレッド③
        buy_execute=sell_execute=False
        possition='none'
        while len(self.trade) >= 15:
            time.sleep(15)
        while True:
            #ポジション無しの場合
            if possition == 'none':
                #口座情報取得
                possition='buy&sell'
            #両ポジションの場合
            elif possition == 'buy&sell':
                #約定履歴取得
                #両注文が約定
                if (sell_execute == True) and (buy_execute == True):
                    possition='none'
                elif sell_execute == True:
                    pass
                elif buy_execute == True:
                    pass
                time.sleep(5)
            #買いポジションの場合
            elif possition == 'buy':
                #約定履歴取得
                if sell_execute == True:
                    possition='none'
            #売りポジションの場合
            elif possition == 'sell':
                #約定履歴取得
                if buy_execute == True:
                    possition='none'
            print(possition)
            time.sleep(5)
    
