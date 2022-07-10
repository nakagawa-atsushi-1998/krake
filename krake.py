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
        pass
        #self.gui=gui.GUI(tkinter.Tk())

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
            #executor.submit(self.gui.main)

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


