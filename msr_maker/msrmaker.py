
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal, MarketSupply, AccountSupply
from itertools import groupby
from math import *
from decimal import Decimal
from markets.log import logger
from markets.marketmaker import MarketMaker
from builtins import NotImplementedError



class MSRMaker(MarketMaker):
    
    # The liquidity parameter (b) 
    liquidity = 5

    def __init__(self, b=5):
        """Creates a new Log market scoring rule maker with the specified liquidity parameter b. """
        self.b = b

    def log_cost(self, supply):
        """Evaluates the risk (also cost) of holding the given supply. """
        return to_decimal(self.liquidity * log(sum(exp(s / self.liquidity) for s in supply)))


    def sample_prices(self, ev, d = 1):
        """
        Samples the prices for each of the events' outcomes. 
        Returns a dict with tuples for the buy/sell prices. 
        """

        # get the supply and the current risk
        supply = MarketSupply.for_event(ev)
        current_risk = self.log_cost(supply.values())
        prices = {}

        # loop over each outcome (variable)
        for (out, amount) in supply.items():

            starting_supply = supply[out]
            assert starting_supply == supply[out]

            supply[out] -= d
            buy = self.log_cost(supply.values()) - current_risk
            supply[out] += 2 * d
            sell = self.log_cost(supply.values()) - current_risk
            supply[out] -= d

            prices[out] = (buy, sell)

            assert starting_supply == supply[out]
        return prices

    @transaction.atomic
    def order_placed(self, ord):
        "Handles creation of orders. "

        assert (not ord.is_processed())

        acc = ord.account
        order_ev_pos = ord.group_by_event()

        # get the cost for completing the order
        cost = sum([self.eval_cost(ev, ps) for (ev,ps) in order_ev_pos])
        logger.debug("Order '%s' total sum: %f" % (ord, cost))

        # see if the order can be completed
        ord.is_successful = (acc.funds >= cost)
        if ord.is_successful:

            # update the market maker amounts
            MarketSupply.accept_order(ord)

            # update the account amounts
            AccountSupply.accept_order(ord)

            # deduct the total transaction cost from the account
            acc.funds -= cost
                    
            # sample buy/sell prices
            for (ev, ps) in order_ev_pos:
                prices = self.sample_prices(ev)
                # and update our offers
                for (out, (b, s)) in prices.items():
                    out.sell_offer = b  # user can sell at our buy price
                    out.buy_offer = s   # user can buy at our sell price
                    out.save()
                    print("b: %f s: %f" % (b, s))
            # TODO: add shares to the user?

        ord.set_processed()
        acc.save()
        ord.save()
        logger.debug("Order '%s' processed!" % (ord,))
            


    def can_quote(self):
        return True

    def price_quote(self, ord):
        """Gets the estimated price for the given order. """
        ps = ord.group_by_event()
        cost = sum([self.eval_cost(ev, ps) for (ev,ps) in order_ev_pos])
        logger.debug("Order '%s' quote: %f" % (ord, cost))
        return cost

    def eval_cost(self, ev, ps):
        "Gets the cost of accepting the given order represented as a list of positions. "
        # eval current risk for the maker
        supply = MarketSupply.for_event(ev)
        current_risk = self.log_cost(supply.values())
        # get the supply after completing the trade
        for p in ps:    
            assert (p.outcome in supply)
            supply[p.outcome] -= p.amount
        # and eval the new risk with it
        new_risk = self.log_cost(supply.values())    
        # cost is the difference in risk
        return new_risk - current_risk

    def end_challenge(self, datum):
        """Distributes the monney!"""
        raise NotImplementedError()