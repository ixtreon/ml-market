
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal
from msr_maker.models import MsrSupply
from itertools import groupby
from math import *
from decimal import Decimal
from markets.log import logger


# The liquidity parameter b. 
b = 5

def log_C(b, supply):
    return to_decimal(b * log(sum(exp(s / b) for s in supply)))

class OrderBook():
        
    def accept_positions(ev, ps):
        "Subtracts the amounts from the given positions from the market maker's balance. "
        #for p in ps:


    def on_order_placed(sender, **kwargs):
        "Handles creation of orders by processing them instantly. "
        # does transaction.atomic() serve as a lock? 

        ord = kwargs['order']
        acc = ord.account
        assert (not ord.is_processed)

        with transaction.atomic():
            logger.info("Processing order '%s' from user '%s' placed at '%s'. " % 
                        (str(ord), str(acc.user), ord.timestamp))
            logger.debug("Order '%s' total sum: %f" % (ord, cost))

            logger.debug("Order '%s' processed!" % (ord,))

    def connect(self):
        "Starts listening for orders by connecting to the 'order_placed' signal. "

        order_placed.connect(self.on_order_placed)

    def disconnect(self):
        "Disconnects from the 'order_placed' signal and stops listening for new orders. "
        order_placed.disconnect(self.on_order_placed)