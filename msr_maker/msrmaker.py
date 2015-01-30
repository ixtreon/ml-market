
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal
from msr_maker.models import MsrSupply
from itertools import groupby
from math import *
from decimal import Decimal
from markets.log import logger
from markets.marketmaker import MarketMaker



class MSRMaker(MarketMaker):
        
    
    # The liquidity parameter b. 
    b = 5

    def __init__(self, b=5):
        """Creates a new Log market scoring rule maker with the specified liquidity parameter b. """
        self.b = b

    def log_cost(self, supply):
        """Evaluates the risk (also cost) of holding the given supply. """
        return to_decimal(self.b * log(sum(exp(s / self.b) for s in supply)))

    def accept_positions(self, ev, ps):
        """Subtracts the amounts from the given positions from the market maker's balance. """
        for p in ps:
            supply = MsrSupply.objects.get(outcome=p.outcome)
            supply.amount += p.amount
            supply.save()

    def sample_prices(self, ev, d = 1):
        """
        Samples the prices for each of the events' outcomes. 
        Returns a dict with tuples for the buy/sell prices. 
        """

        supply = MsrSupply.for_event(ev)
        current_risk = self.log_cost(supply.values())
        prices = {}
        #s = sum([exp(amount/b) for (out, amount) in supply.items()])
        for (out, amount) in supply.items():
            ## calculate the instantaneous price
            #buy = sell = exp(amount/b) / s

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


    def order_placed(self, ord):
        "Handles creation of orders by processing them instantly. "
        # TODO: implement a queue?
        # also: does transaction.atomic() serve as a lock? 

        acc = ord.account
        assert (not ord.is_processed())

        with transaction.atomic():
            event_positions = self.order_positions(ord)

            # get the cost for completing the order by using the log-msr
            cost = sum([self.eval_cost(ev, ps) for (ev,ps) in event_positions])
            logger.debug("Order '%s' total sum: %f" % (ord, cost))

            # see if the order can be completed
            ord.is_successful = (acc.funds >= cost)
            if ord.is_successful:
                # if so, deduct credits
                acc.funds -= cost

                # update the market maker amounts
                for (ev, ps) in event_positions:
                    self.accept_positions(ev, ps)
                    
                # sample buy/sell prices
                for (ev, ps) in event_positions:
                    prices = self.sample_prices(ev)
                    # and update our offers
                    for (out, (b, s)) in prices.items():
                        out.sell_offer = b  # user can sell at our buy price
                        out.buy_offer = s   # user can buy at our sell price
                        print("b: %f s: %f" % (b, s))
                        out.save()
                # TODO: add shares to the user?

            ord.set_processed()
            acc.save()
            ord.save()
            logger.debug("Order '%s' processed!" % (ord,))
            
    def can_quote(self):
        return True

    def price_quote(self, ord):
        ps = self.order_positions(ord)
        cost = sum([self.eval_cost(ev, ps) for (ev,ps) in event_positions])
        logger.debug("Order '%s' quote: %f" % (ord, cost))
        return cost

    def order_positions(self, ord):
        """
        Gets all positions in the given order. 
        Returns a dictionary of the events with the list of positions for each. 
        """
        all_ps = list(ord.position_set.all())

        get_ev_id = lambda p: p.outcome.event.id
        all_ps.sort(key=get_ev_id)
        return [(ev,list(ps)) for (ev,ps) in groupby(all_ps, key=lambda p: p.outcome.event)]

    def eval_cost(self, ev, ps):
        "Gets the cost of accepting the given order represented as a list of positions. "
        # eval current risk
        supply = MsrSupply.for_event(ev)
        current_risk = self.log_cost(supply.values())
        # obtain the new supply
        for p in ps:    
            assert (p.outcome in supply)
            supply[p.outcome] -= p.amount
        # and eval risk for it
        new_risk = self.log_cost(supply.values())    
        # cost is the difference in risk
        return new_risk - current_risk