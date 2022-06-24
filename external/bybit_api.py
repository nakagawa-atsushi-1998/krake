from pybit.inverse_perpetual import HTTP

class HttpClient():
    def __init__(
        self,
        symbol='BTCUSD',
    ):
        self.url='https://api.bybit.com' #self.url='https://api-testnet.bybit.com'
        self.symbol=symbol
        
    def authenticate(
        self,
        api_key,
        api_secret
    ):
        self.session = HTTP(
            self.url,
            api_key=api_key,
            api_secret=api_secret
        )

    def fetch_candle(
        self,
        time_scale,
        start_time
    ):
        result_list_string = self.session.query_kline(
            symbol=self.symbol,
            interval=time_scale,
            from_time=start_time
        )
        result_list = list(result_list_string['result'])
        return result_list
