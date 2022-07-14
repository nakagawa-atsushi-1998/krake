#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
import time
import json
import hmac
import hashlib
from wsgiref.handlers import format_date_time
import requests
import websocket
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('Agg') #matplotlib.use('tkagg')
import warnings; warnings.simplefilter('ignore')
import os; cd=os.path.dirname(__file__); os.chdir(cd)
from .model import (
    account,
    crypto,
    order
)

aCol=account.Account.Column()
cCol=crypto.Crypto.Column()
oCol=order.Order.Column()

class Path:
    rate='/api/exchange/orders/rate'
    trades='/api/trades'
    order='/api/exchange/orders'
    balance='/api/accounts/balance'
    transaction='/api/exchange/orders/transactions'
    cancel_status='/api/exchange/orders/cancel_status'
    unsettled_order='/api/exchange/orders/opens'

class WebsocketClient:
    def __init__(self):
        self.pair='btc_jpy'
        #time_scale_list=[1,5,15,30]
        self.WURL='wss://ws-api.coincheck.com/'
        self.storage_term=60 #保存期間
        self.request_json = json.dumps({
            'type':'subscribe', 
            'channel':'btc_jpy-trades'
        })
        self.lock=threading.Lock()
        self.order=order.Order()
        self.crypto=crypto.Crypto()
        self.account=account.Account()

    def connect(self):  #スレッド①
        self.session=websocket.WebSocketApp(
            self.WURL,
            on_open=self.__on_open,
            on_close=self.__on_close,
            on_error=self.__on_error,
            on_message=self.__on_message,
        )
        print('session connect.')
        self.session.run_forever()
    #接続
    def __on_open(self, ws):
        self.__opened=True
        self.session.send(
            self.request_json)
        print('opened.')
    #接続エラー
    def __on_error(self, ws, error):
        print('incorrect.')
        self.__reconnect()
    #再接続
    def __reconnect(self):
        self.__exit()
        time.sleep(1)
        self.connect()
    #離脱時
    def __exit(self):
        self.session.close()
    #切断時
    def __on_close(self, ws):
        print('session closed.')
    #メッセージ受信時
    def __on_message(self, ws, message):
        trade_dict=self.crypto.form_trade(message)
        self.crypto.trade=self.crypto.trade.append(
            trade_dict,
            ignore_index=True)
        time.sleep(0.25)
        print(*self.crypto.trade.values[-1])

    def cast(self):  #スレッド②
        while True:
            now=datetime.datetime.now()
            self.start_time=datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, 0
            )
            self.end_time=datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, 0
            )+datetime.timedelta(minutes=1)
            while datetime.datetime.now() < self.end_time:
                time.sleep(1)
            self.lock.acquire() #施錠
            self.crypto.cast_ohlcv(self.start_time)
            print(self.crypto.ohlcv[-1:])
            self.lock.release() #施錠
            #self.plot_graph()
            #if len(self.ohlcv) >= 15:
            #    self.calculate_bb()
            #    print(self.bb)

class HttpClient(WebsocketClient):
    def __init__(self, websocket_client):
        #super().__init__(websocket_client)
        super().__init__()
        self.URL='https://coincheck.com'

    def authenticate(self, access_key, secret_key):
        self.__access_key=access_key
        self.__secret_key=secret_key
        print('authenticated API.')

    def gain_signature(self, message):
        signature=hmac.new(
            bytes(self.__secret_key.encode('ascii')),
            bytes(message.encode('ascii')),
            hashlib.sha256
        ).hexdigest()
        return signature

    def gain_header(self, nonce, signature):
        header = {
            'ACCESS-KEY':self.__access_key,
            'ACCESS-NONCE':nonce,
            'ACCESS-SIGNATURE':signature,
            'Content-Type':'application/json'
        }
        return header

    def get(self, path, params=None):
        if params != None:
            params=json.dumps(params)
        else:
            params=''
        nonce=str(int(time.time()))
        message=nonce+self.URL+path+params
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.get(
            self.URL+path,
            headers=headers
        ).json()

    def post(self, path, params):
        params=json.dumps(params)
        nonce=str(int(time.time()))
        message=nonce+self.URL+path+params
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.post(
            self.URL+path,
            data=params,
            headers=headers
        ).json()

    def delete(self, path):
        nonce=str(int(time.time()))
        message=nonce+self.URL+path
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.delete(
            self.URL+path,
            headers=headers
        ).json()

    def get_unsettled_order(self):
        path=Path.unsettled_order
        return self.get(path)

    def get_cancel_status(self, _id=None):
        path=Path.cancel_status+'?id='+str(_id)
        return self.get(path)

    def get_transaction(self):
        path=Path.transaction
        return self.get(path)['transactions']
    
    def form_transaction(self, tran_list):
        self.tran_df=pd.DataFrame(columns=oCol.past)
        for tran in tran_list:
            tran_dict={
                'Datetime':datetime.datetime.strptime(tran['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')+datetime.timedelta(hours=9),
                'ID':tran['order_id'],
                'Type':tran['side'],
                'Rate':float(tran['funds']['jpy']),
                'Amount':float(tran['funds']['btc'])
            }
            self.tran_df=self.tran_df.append(tran_dict, ignore_index=True)
        return self.tran_df

    def get_balance(self):
        path=Path.balance
        return self.get(path)

    def get_balance_until_true(self):
        path=Path.balance
        while True:
            result=self.get(path)
            if result['success']==True:
                break
            print('get balance until true.')
            time.sleep(1)
        return result

    def get_rate(self):
        path='/api/rate/'+self.pair
        return requests.get(
            self.URL+path
        ).json()
    
    def get_trade_list(
        self,
        limit=None,
        order='desc',
        starting_after=None,
        ending_before=None
    ):
        path=Path.trades
        params={
            'limit':limit,
            'starting_before':starting_after,
            'ending_after':ending_before,
            'order':order,
            'pair':self.pair
        }
        return requests.get(
            self.URL+path,
            params=params
        ).json()['data']

    def split_trades_into_ohlcv(self, trades):
        while True:
            if len(trades) == 0:
                break
            dt=trades['Datetime'].iloc[0]
            start_time=datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day,
                hour=dt.hour, minute=dt.minute, second=0)
            end_time=start_time+datetime.timedelta(minutes=1)
            self.crypto.trade=trades.query('@start_time <= Datetime < @end_time')
            trades=trades.query('@end_time <= Datetime')
            print(start_time)
            print(self.crypto.trade)
            if len(trades) != 0:
                self.crypto.cast_ohlcv(start_time)
                trades.reset_index()
            else:
                pass

    def post_order_buy(
        self,
        rate,
        amount,
        order_type='buy',
        #stop_loss_rate=None,
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'rate':rate,
            'amount':amount
        }
        return self.post(
            path,
            params)

    def post_order_sell(
        self,
        rate,
        amount,
        order_type='sell',
        #stop_loss_rate=None
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'rate':rate,
            'amount':amount
        }
        return self.post(
            path,
            params)

    def post_market_buy(
        self,
        market_buy_amount, #金額
        order_type='market_buy'
    ):
        path=Path.order
        params = {
            'pair':self.pair,
            'order_type':order_type,
            'market_buy_amount':market_buy_amount,
        }
        return self.post(
            path,
            params)

    def post_market_sell(
        self,
        amount, #量
        order_type='market_sell',
        #stop_loss_rate=None
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'amount':amount
        }
        return self.post(
            path,
            params)

    """
    def post_order(
        self,
        order_type=None,
        rate=None,
        amount=None,
        market_buy_amount=None,
        #stop_loss_rate=None
    ):
        path = Path.order
        if (rate != None) and (amount != None):
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'rate':rate,
                'amount':amount,
            }
        elif market_buy_amount != None:
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'market_buy_amount':market_buy_amount,
            }
        elif amount != None:
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'amount':amount
            }
        return self.post(
            path,
            params
        )
        """

    def delete_order(self, _id=None):
        path = Path.balancepath.order + str(_id)
        return self.delete(path)

