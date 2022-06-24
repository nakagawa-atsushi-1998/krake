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
        self.URL=URL.domain
        self.pair:str=pair
        self.price:float=price
        self.amount:float=amount

    def authenticate(self, access_key, secret_key):
        self.__access_key = access_key
        self.__secret_key = secret_key

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
        message = nonce + self.URL+path+params
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
            self.URL+path,
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
                'pair':self.pair,
                'order_type':order_type,
                'rate':rate,
                'amount':amount,
                'id':_id
            }
        elif market_buy_amount != None:
            params = {
                'pair':self.pair,
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
            self.URL+path,
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
            self.URL+path,
            params=params
        ).json()
