import pandas as pd
import matplotlib.pyplot as plt
import configure
from external import (
    bybit_api,
    coincheck_api,
    line_api,
)

class Orderer:
    def __init__(self):
        self.b=None
        
    def prepare(self):
        self.b_client=bybit_api.HttpClient()
        self.c_client=coincheck_api.HttpClient()
        self.l_client=line_api.Client()
        
        
    def work(self):
        pass
    
    def collect(self):
        pass
    
    def predict(self):
        pass
    
    def plot(self):
        pass
    
    def judge(self):
        pass

def main():
    orderer=Orderer()

if __name__ == "__main__":
    main()