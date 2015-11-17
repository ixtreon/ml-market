    
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal, MarketBalance
from itertools import groupby
from math import *
from decimal import Decimal
from markets.log import logger



class OrderBook():
        
    def match_position(self, pos):
        """
        Returns the amount of shares remaining unprocessed in the given position, 
        after matching it with all suitable of the opposite type. 

        Each successful trade is recorded in the form of a new Order with the same signature as the original one. 
        """
        matches = outcome.position_set.filter(is_processed=False)
        if pos.amount > 0:  # want to purchase, seek lower prices, normal order
            matches = matches.filter(contract_price__lte=pos.price, amount__lte=0).order_by('contract_price')
        else:   # sell, seek greater prices, reverse order
            matches = outcome.position_set.filter(contract_price__gte=pos.price, amount__lte=0).order_by('-contract_price')

        ps = []
        amount_left = abs(pos.amount)

        for other_p in matches:
            if amount_left <= 0:
                break
            amount_completed = abs(p.partial_complete(other_p))
            assert amount_completed < amount_left
            amount_left -= amount_completed
        return amount_left


    @transaction.atomic
    def order_placed(self, ord):
        "Handles the processing of orders by matching them with orders of the opposite type. "
        # does transaction.atomic() serve as a lock? 

        assert (not ord.is_processed())

        positions_fulfilled = {}

        for (ev, ps) in ord.group_by_event():
            for p in ps:
                self.match_position(p)

            self.update_prices(ev)


    def can_quote(self):
        return False

    def update_prices(self, ev):
        print("update prices")
        for out in ev.outcomes.all():
            # get the lowest sell offer
            try:
                low = out.position_set.filter(is_processed=False, amount__lte=0).order_by('contract_price')[0].contract_price
            except:
                low = Decimal('NaN')
            out.sell_offer = low

            # get the highest buy offer
            try:
                hi = out.position_set.filter(is_processed=False, amount__gte=0).order_by('-contract_price')[0].contract_price
            except:
                hi = Decimal('NaN')
            out.buy_offer = hi
        pass

    def end_challenge(self, c):
        pass