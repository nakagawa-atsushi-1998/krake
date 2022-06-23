#!/usr/bin/env python
# coding: utf-8

# In[3]:


# 共通
import sys, enum
import csv, json
import time, datetime
# HttpConnectorのみ利用
import hmac
import hashlib
import requests
# WebsockConnectorのみ利用
import websocket
import concurrent.futures
import numpy as np
import pandas as pd
#import mplfinance as mpf
import matplotlib.pyplot as plt



class URL:
    domain='https://coincheck.com'
    class path:
        order='/api/exchange/orders'
        unsettled_order='/api/exchange/orders/opens'
        cancel_status='/api/exchange/orders/cancel_status'
        transaction='/api/exchange/orders/transactions'
        balance='/api/accounts/balance'
        rate='/api/exchange/orders/rate'

class HttpClient:
    def __init__(
        self,
        pair='btc_jpy',
        price=3000000,
        amount=1.0
    ):
        self.url=URL.domain
        self.pair:str=pair
        self.price:float=price
        self.amount:float=amount

    def auth(self, access_key, secret_key):
        self.__access_key = access_key
        self.__secret_key = secret_key
    #private   
    def gain_signature(self, message):
        signature = hmac.new(
            bytes(self.__secret_key.encode('ascii')),
            bytes(message.encode('ascii')),
            hashlib.sha256
        ).hexdigest()
        return signature

    def gain_header(self, nonce, signature):
        header = {
            'ACCESS-KEY': self.__access_key,
            'ACCESS-NONCE': nonce,
            'ACCESS-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        return header

    def get(self, path, params=None):
        if params != None:
            params = json.dumps(params)
        else:
            params = ''
        nonce = str(int(time.time()))
        message = nonce + self.url + path + params
        signature = self.gain_signature(message)
        headers = self.gain_header(nonce, signature)
        return requests.get(
            self.host+path,
            headers=headers
        ).json()

    def post(self, path, params):
        params = json.dumps(params)
        nonce = str(int(time.time()))
        message = nonce + self.url + path + params
        signature = self.gain_signature(message)
        headers = self.gain_header(nonce, signature)
        return requests.post(
            self.url+path,
            data=params,
            headers=headers
        ).json()

    def delete(self, path):
        nonce = str(int(time.time()))
        message = nonce + self.host + path
        signature = self.gain_signature(message)
        headers = self.gain_header(nonce, signature)
        return requests.delete(
            self.url+path,
            headers = headers
        ).json()

    def post_order(
        self,
        order_type=None,
        rate=None,
        amount=None,
        market_buy_amount=None,
        _id=1
    ):
        path = URL.suffix.order
        if rate != None and amount != None:
            params = {
                'pair':pair,
                'order_type':order_type,
                'rate':rate,
                'amount':amount,
                'id':_id
            }
        elif market_buy_amount != None:
            params = {
                'pair':pair,
                'order_type':order_type,
                'market_buy_amount':market_buy_amount,
                'id':_id
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
    
    def get_unsettled_order(self):
        path = URL.path.unsettled_order
        return self.get(path)

    def delete_order(self, _id=1):
        path = URL.path.order + str(_id)
        return self.delete(path)

    def get_cancel_status(self, _id=1):
        path = URL.path.cancel_status+'?id=' + str(_id)
        return self.get(path)

    def get_transaction(self):
        path = URL.path.transaction
        return self.get(path)

    def get_balance(self):
        path = URL.path.balance
        return self.get(path)
    
    #public
    def get_rate(self):
        path = '/api/rate/' + self.pair
        return requests.get(
            self.host+path
        ).json()
    
    def get_amount(
        self,
        order_type:str,
        price=None
    ):
        path = URL.path.rate
        params = {
            'order_type':order_type,
            'pair':self.pair,
            'price':price
        }
        return requests.get(
            self.url+path,
            params=params
        ).json()
    
    def get_price(
        self,
        order_type:str,
        amount=None,
    ):
        path = URL.path.rate
        params = {
            'order_type':order_type,
            'pair':self.pair,
            'amount':amount
        }
        return requests.get(
            self.url+path,
            params=params
        ).json()



class WebsocketClient:
    def __init__(self):
        self.url:str = 'wss://ws-api.coincheck.com/'
        self.status:str = ''
        self.pair = 'btc_jpy'
        self.ask = self.ask_volume = None
        self.bid = self.bid_volume = None
        self.figure, self.ax = plt.subplots(); plt.ion()
        self.exec = concurrent.futures.ThreadPoolExecutor()
        self.rate = pd.DataFrame(columns=columns['rate'])
        self.ask_ohlc = pd.DataFrame(columns=columns['ohlc'])
        self.bid_ohlc = pd.DataFrame(columns=columns['ohlc'])
        
    @property
    def pair(self):
        pass
    @pair.setter
    def pair(self, pair):
        self.__pair:str = pair
        self.__request = {
            'type':'subscribe', 
            'channel':pair+'-trades'
        }

    def connect(self):
        self.status = 'connect'; print(self.status)
        #self.__connected = False
        #self.__opened = False
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open = self.__on_open,
            on_close = self.__on_close,
            on_error = self.__on_error,
            on_message = self.__on_message,
        )
        self.exec.submit(self.ws.run_forever)
        self.exec.submit(self.__stats)
        
    def __reconnect(self):
        self.status = 'reconnect'; print(self.status)
        self.__exit()
        time.sleep(3)
        self.connect()

    def __exit(self):
        self.status = 'exit'; print(self.status)
        self.ws.close()

    def __on_open(self, ws):
        self.status = 'open'; print(self.status)
        self.ws.send(json.dumps(self.__request))
        self.__opened = True

    def __on_error(self, ws, error):
        self.status = 'error'; print(self.status)
        self.__reconnect()

    def __on_close(self, ws):
        self.status = 'close'; print(self.status)

    def __on_message(self, ws, message):
        trade = self.__form_message(message)
        self.__collect(trade)

    def __form_message(self, message):
        elements = message.strip('[ ]').replace('"', '').split(',')
        trade = {
            'id': int(elements[0]),
            'type': elements[4],
            'price': float(elements[2]),
            'volume': float(elements[3]),
        }
        time.sleep(1)
        return trade
    
    def __collect(self, trade):
        dt = datetime.datetime.now()
        self.dt = datetime.datetime.strptime(dt.strftime(system['form'])[:-4], system['form'])
        if trade['type'] == 'buy':
            self.ask = trade['price']
            self.ask_volume = trade['volume']
        elif trade['type'] == 'sell':
            self.bid = trade['price']
            self.bid_volume = trade['volume']
        print(self.dt, self.ask, self.bid)
        self.rate = self.rate.append(
            {
                columns['rate'][0]:self.dt,
                columns['rate'][1]:self.ask,
                columns['rate'][2]:self.bid,
                columns['rate'][3]:self.ask_volume,
                columns['rate'][4]:self.bid_volume
            },
            ignore_index=True
        )

    def __stats(self):
        while True:
            now = datetime.datetime.now()
            start_time = datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, 0
            )
            end_time = datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute+1, 0
            )
            while datetime.datetime.now() < end_time:
                time.sleep(0.5)
            ask_open = self.rate['Ask'].values[1]
            ask_close = self.rate['Ask'].values[-1]
            ask_high = self.rate['Ask'].max()
            ask_low = self.rate['Ask'].min()
            ask_volume = self.rate['AskVolume'].sum()
            self.ask_ohlc = self.ask_ohlc.append(
                {
                    columns['ohlc'][0]: start_time,
                    columns['ohlc'][1]: ask_open,
                    columns['ohlc'][2]: ask_high,
                    columns['ohlc'][3]: ask_low,
                    columns['ohlc'][4]: ask_close,
                    columns['ohlc'][5]: ask_volume
                },
                ignore_index=True
            )
            #print(self.ohlc.values[-1])
            self.__plot()
            self.__forget()

    def __forget(self):
        self.rate = pd.DataFrame(columns=columns['rate'])
        pass

    def __record(self):
        pass
    
    def __plot(self):
        plt.cla()
        self.ax.plot(
            self.ask_ohlc['Date'],
            self.ask_ohlc['Close'],
            color=system['color']['ask'][0]
        )
        self.ax.plot(
            self.bid_ohlc['Date'],
            self.bid_ohlc['Close'],
            color=system['color']['bid'][0]
        )
        plt.show()

