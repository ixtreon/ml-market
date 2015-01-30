
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal
from msr_maker.models import MsrSupply
from itertools import groupby
from math import *
from decimal import Decimal
from markets.log import logger



class OrderBook():
        

    def order_placed(self, ord):
        "Handles creation of orders by matching them, if possible. "
        # does transaction.atomic() serve as a lock? 

        assert (not ord.is_processed())

        acc = ord.account

        #ord.position_set.filter(is_processed=False)

        with transaction.atomic():
            logger.debug("Order '%s' total sum: %f" % (ord, cost))

            logger.debug("Order '%s' processed!" % (ord,))

        raise NotImplementedError()

            
    def can_quote(self):
        return False