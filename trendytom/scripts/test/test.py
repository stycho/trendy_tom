#!/usr/bin/env python

from trendytom.traders.bitmex_trader import Bitmex

BITMEX_API_KEY = ""
BITMEX_API_SECRET = ""

client = Bitmex(BITMEX_API_KEY, BITMEX_API_SECRET,use_testnet=False)
client.test_buy()
