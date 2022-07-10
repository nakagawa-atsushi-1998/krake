import numpy as np
import pandas as pd

class Account:
    class Column:
        balance=[
            'Datetime',
            'JPY',
            'BTC',
        ]

    def __init__(
        self
    ):
        self.balance=pd.DataFrame(columns=self.Column.balance)
