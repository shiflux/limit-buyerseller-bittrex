import bt_api
from bt_api import Bittrex
from time import sleep

class LimitBuyer:

    def __init__(self, market, maxquantity, pricelimit, stepincrease, apikey, apisecret, updatetime=5):
        self.market = market
        self.maxquantity = maxquantity
        self.pricelimit = pricelimit
        self.stepincrease = stepincrease
        self.apikey = apikey
        self.apisecret = apisecret
        self.api = Bittrex(self.apikey, self.apisecret)
        self.updatetime = updatetime
        self.orderprice = None

    def start(self):
        while(True):
            sleep(self.updatetime)
            currentprice = self.get_current_price()
            if currentprice is None or currentprice >= self.pricelimit:
                print("Price too high", currentprice)
                continue

            if not self.check_open_order(): #reset if there are no open orders
                self.orderprice = None

            if self.orderprice is None or self.orderprice < currentprice: #open order
                if self.orderprice is not None: #cancel order if there are any open
                    self.cancel_open_orders()
                self.orderprice = currentprice + self.stepincrease
                self.open_order(self.orderprice)

    def get_current_price(self):
        response = self.api.get_orderbook(self.market, bt_api.BUY_ORDERBOOK)
        if response["result"] is None:
            return  None

        return response["result"][0]["Rate"]

    def cancel_open_orders(self):
        response = self.api.get_open_orders(self.market)
        if len(response["result"]) is 0:
            return
        else:
            for r in response["result"]:
                self.api.cancel(r["OrderUuid"])

    def open_order(self, price):
        response = self.api.get_open_orders(self.market, self.maxquantity, price)
        if response["success"]:
            print("Order placed")
        else:
            print("Error placing order", response["message"])

    def check_open_order(self):
        response = self.api.get_open_orders(self.market)
        print response
        if len(response["result"]) is 0:
            return False
        else:
            return True
