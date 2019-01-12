import math
import bitmex


class Bitmex():
    def __init__(self, api_key, api_secret, use_testnet=True,
                 leverage_multiplier=2.5, stop_loss_percentage=0.02,
                 symbol="XBTUSD"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.leverage_multiplier = leverage_multiplier
        self.stop_loss_percent = stop_loss_percentage
        self.symbol = symbol

        self.client = bitmex.bitmex(
                test=use_testnet,
                api_key=self.api_key,
                api_secret=self.api_secret)

    def get_order_book(self):
        order_book = self.client.OrderBook.OrderBook_getL2(symbol=self.symbol)
        result = order_book.result()[0]
        return result

    def get_bid_price(self):
        def filter_buy(order):
            return order["side"] == "Buy"

        buy_orders = list(filter(filter_buy, self.get_order_book()))
        bid_order = max(buy_orders, key=lambda x: x['price'])
        return bid_order["price"]

    def get_ask_price(self):
        def filter_sell(order):
            return order["side"] == "Sell"

        sell_orders = list(filter(filter_sell, self.get_order_book()))
        ask_order = min(sell_orders, key=lambda x: x['price'])

        return ask_order["price"]

    def get_balance(self):
        wallet = self.client.User.User_getWallet().result()[0]
        amount = wallet['amount']
        return amount

    def get_current_position(self):
        return self.client.Position.Position_get().result()[0][0]['currentQty']

    def is_in_position(self):
        position = self.get_current_position()
        is_in_position = True if position != 0 else False
        return is_in_position

    def is_going_long(self):
        position = self.get_current_position()
        return position > 0

    def is_going_short(self):
        position = self.get_current_position()
        return position < 0

    def get_all_free_money(self):
        wallet = self.client.User.User_getWallet().result()[0]
        free_money = wallet
        return free_money

    def set_long_stoploss(self, price, amount):
        return

    def close_all_positions(self):
        res1 = self.client.Order.Order_new(
                symbol=self.symbol,
                execInst='Close',
                side='Sell').result()[0]
        res2 = self.client.Order.Order_new(
                symbol=self.symbol,
                execInst='Close',
                side='Buy').result()[0]
        return (res1, res2)

    def cancel_all_orders(self):
        return self.client.Order.Order_cancelAll().result()[0]

    def go_long(self):
        # Close all positions and cancel orders
        self.close_all_positions()
        self.cancel_all_orders()

        # Calculate order size
        order_size = self.order_size_long()

        # Buy order
        market_sell_result = self.client.Order.Order_new(
                symbol=self.symbol,
                orderQty=order_size,
                ordType='Market',
                side='Buy').result()[0]

        # Calculate stop loss
        order_avg_price = market_sell_result["avgPx"]
        stop_loss_price = self.stop_loss_long(order_avg_price)

        # Stop loss order
        self.client.Order.Order_new(
                symbol=self.symbol,
                orderQty=order_size,
                ordType='Stop',
                stopPx=stop_loss_price,
                side='Sell').result()

    def go_short(self):
        # Close all positions and cancel orders
        self.close_all_positions()
        self.cancel_all_orders()

        # Calculate order size
        order_size = self.order_size_short()

        # Sell order
        market_buy_result = self.client.Order.Order_new(
                symbol=self.symbol,
                orderQty=order_size,
                ordType='Market',
                side='Sell').result()[0]

        # Calculate stop loss
        order_avg_price = market_buy_result["avgPx"]
        stop_loss_price = self.stop_loss_short(order_avg_price)

        # Stop loss order
        result = self.client.Order.Order_new(
                symbol=self.symbol,
                orderQty=order_size,
                ordType='Stop',
                stopPx=stop_loss_price,
                side='Buy').result()

    def order_size_long(self):
        balance = self.get_balance() / 100000000
        order_price = self.get_ask_price()
        order_size = (balance * order_price) * self.leverage_multiplier
        return math.floor(order_size)

    def order_size_short(self):
        balance = self.get_balance() / 100000000
        order_price = self.get_bid_price()
        order_size = (balance * order_price) * self.leverage_multiplier
        return math.floor(order_size)

    def stop_loss_long(self, order_price):
        return math.floor(order_price * (1 - self.stop_loss_percent))

    def stop_loss_short(self, order_price):
        return math.floor(order_price * (1 + self.stop_loss_percent))

    def test_buy(self):
        order_size = 1
        # Sell order
        market_buy_result = self.client.Order.Order_new(
                symbol=self.symbol,
                orderQty=order_size,
                ordType='Market',
                side='Buy').result()[0]
