import tkinter
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor
)
import configure
import gui
import crypto
import coincheck_api
import line_notify_api

#import warnings
#warnings.simplefilter('ignore')

class Orderer:
    def __init__(
        self,
    ):
        self.basic_price:float #基準値
        self.tolerance_pct:float #許容誤差比率
        self.upper_tolerance:float #許容上限値
        self.lower_tolerance:float #許容下限値
        self.gui=gui.GUI(tkinter.Tk())
        self.figure, self.axes = plt.subplots(3, 1, figsize=(7.0, 8.0))
        plt.ion()

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

    def initialize_data(
        self,
    ):
        trades=self.cchc.get_trades(
            limit=100,
        )
        trade_df, start_id, end_id=self.cchc.form_trades(trades)
        print(trade_df); print(start_id, end_id)
        self.cchc.split_trades_into_ohlcv(trade_df)

    def mainloop(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.ccwc.connect)
            executor.submit(self.ccwc.collect)
            #executor.submit(self.gui.main)

def main():
    orderer=Orderer()
    orderer.give_key_to_api(
        KEY.COINCHECK_API_ACCESS,
        KEY.COINCHECK_API_SECRET,
        KEY.LINE_API_TOKEN,
    )
    orderer.initialize_data()
    time.sleep(10)
    orderer.mainloop()

if __name__ == "__main__":
    KEY = configure.KEY
    PATH = configure.PATH
    COLOR = configure.FORM.COLOR
    ALPHA = configure.FORM.alpha
    LABEL = configure.FORM.label
    main()
