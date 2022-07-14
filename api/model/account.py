import json
import time
import datetime
import numpy as np
import pandas as pd

class Account:
    class Column:
        balance=[
            'Datetime',
            'JPY',
            'BTC',
        ]

    def __init__(self):
        self.balance=pd.DataFrame(columns=self.Column.balance)

    def form_balance(self, balance_):
        datetime_=datetime.datetime.now()
        jpy_=float(balance_['jpy'])
        btc_=float(balance_['btc'])
        balance_dict={
            'Datetime':datetime_,
            'JPY': jpy_,
            'BTC': btc_,
        }
        return balance_dict

    def calc_balance(self, past_df):
        past_df=past_df.sort_values(
            'Datetime', ascending=False)
        for counter in range(len(self.balance), len(past_df)):
            past_lastrow=past_df.iloc[counter]
            balance_lastrow=self.balance.iloc[counter-1]
            datetime_=past_lastrow['Datetime']
            jpy_=balance_lastrow['JPY']+past_lastrow['Rate']
            btc_=balance_lastrow['BTC']+past_lastrow['Amount']
            balance_dict={
                'Datetime':datetime_,
                'JPY':jpy_,
                'BTC':btc_,
            }
            self.balance=self.balance.append(
                balance_dict, ignore_index=True)
        self.balance=self.balance.sort_values(
            'Datetime', ascending=True)



