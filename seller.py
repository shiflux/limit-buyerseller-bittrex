import bt_api
from bt_api import Bittrex
from time import sleep


class LimitSeller:

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
            currentorderbook = self.get_order_book()
            if currentorderbook is None or currentorderbook[0] <= self.pricelimit:
                print("Price too low", currentorderbook[0])
                currentorder = self.check_open_order()
                if currentorder is None:
                    self.open_order(self.pricelimit)
                elif currentorder == currentorderbook[0]:
                    self.cancel_open_orders()
                continue

            open_ord = self.check_open_order()
            if open_ord is None:
                self.orderprice = None

            elif open_ord > currentorderbook[0]:
                self.cancel_open_orders()
                self.orderprice = None

            elif open_ord == currentorderbook[0] and currentorderbook[1]-self.stepincrease*2 > open_ord:
                self.cancel_open_orders()
                self.orderprice = currentorderbook[1] - self.stepincrease
                self.open_order(self.orderprice)
                continue

            if self.orderprice is None: #open order
                self.orderprice = currentorderbook[0] - self.stepincrease
                self.open_order(self.orderprice)

    def get_order_book(self):
        response = self.api.get_orderbook(self.market, bt_api.SELL_ORDERBOOK)
        if response["result"] is None:
            return None

        toret = []
        toret.append(response["result"][0]["Rate"])
        if len(response["result"]) > 1:
            toret.append(response["result"][1]["Rate"])
        return toret


    def cancel_open_orders(self):
        response = self.api.get_open_orders(self.market)
        if len(response["result"]) is 0:
            return
        else:
            for r in response["result"]:
                if r["OrderType"] == "LIMIT_SELL":
                    self.api.cancel(r["OrderUuid"])

    def open_order(self, price):
        buyquantity = self.get_balance()
        if(buyquantity>self.maxquantity):
            buyquantity = self.maxquantity
        response = self.api.sell_limit(self.market, buyquantity, price)
        if response["success"]:
            print("Order placed", price)
        else:
            print("Error placing order", response["message"])

    def check_open_order(self):
        response = self.api.get_open_orders(self.market)
        if len(response["result"]) is 0:
            return None
        else:
            for r in response["result"]:
                if r["OrderType"] == "LIMIT_SELL":
                    return r["Limit"]

    def get_balance(self):
        response = self.api.get_balance(self.market.split('-')[1])
        if response["success"]:
            return response["result"]["Balance"]
        else:
            return -1
