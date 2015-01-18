
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order, to_decimal
from msr_maker.models import Supply
from itertools import groupby
from math import *
from decimal import Decimal


# The liquidity parameter b. 
b = 5

def log_C(b, supply):
    return to_decimal(b * log(sum(exp(s / b) for s in supply)))

class MSRMaker():
        
    def get_ev_pos(ord):
        "Gets all positions in the given order and keys them by their event. "
        all_ps = list(ord.position_set.all())

        get_ev_id = lambda p: p.outcome.event.id
        all_ps.sort(key=get_ev_id)
        return [(ev,list(ps)) for (ev,ps) in groupby(all_ps, key=lambda p: p.outcome.event)]

    def eval_cost(ev, ps):
        "Gets the cost of accepting the given deal represented as a list of positions. "
        # eval current risk
        supply = Supply.for_event(ev)
        current_risk = log_C(b, supply.values())
        # obtain the new supply
        for p in ps:    
            assert (p.outcome in supply)
            supply[p.outcome] -= p.amount
        # and eval risk for it
        new_risk = log_C(b, supply.values())    
        # cost is the difference in risk
        return new_risk - current_risk

    def accept_positions(ev, ps):
        "Subtracts the amounts from the given positions from the market maker's balance. "
        for p in ps:
            supply = Supply.objects.get(outcome=p.outcome)
            supply.amount += p.amount
            supply.save()

    def sample_prices(ev, d = 1):
        "Samples the prices for each of the events' outcomes. Returns a dict with tuples for the buy/sell prices. "
        supply = Supply.for_event(ev)
        current_risk = log_C(b, supply.values())
        prices = {}
        #s = sum([exp(amount/b) for (out, amount) in supply.items()])
        for (out, amount) in supply.items():
            ## calculate the instantaneous price
            #buy = sell = exp(amount/b) / s

            starting_supply = supply[out]
            assert starting_supply == supply[out]

            supply[out] -= d
            buy = log_C(b, supply.values()) - current_risk
            supply[out] += 2 * d
            sell = log_C(b, supply.values()) - current_risk
            supply[out] -= d
            prices[out] = (buy, sell)

            assert starting_supply == supply[out]
        return prices

    def on_order_placed(sender, **kwargs):
        "Handles creation of orders by processing them instantly. "
        # TODO: implement a queue?
        # also: does transaction.atomic() serve as a lock? 

        ord = kwargs['order']
        acc = ord.account
        assert (not ord.is_processed)

        with transaction.atomic():
            logger.info("Processing order '%s' from user '%s' placed at '%s'. " % 
                        (str(ord), str(acc.user), ord.timestamp))
            event_positions = MSRMaker.get_ev_pos(ord)

            # get the cost for completing the order by using the log-msr
            cost = sum([MSRMaker.eval_cost(ev, ps) for (ev,ps) in event_positions])
            logger.debug("Order '%s' total sum: %f" % (ord, cost))
            # see if the order can be completed
            ord.is_successful = (acc.funds >= cost)
            if ord.is_successful:
                # if so, deduct credits
                acc.funds -= cost

                # update the market maker amounts
                for (ev, ps) in event_positions:
                    MSRMaker.accept_positions(ev, ps)
                    
                # sample buy/sell prices
                for (ev, ps) in event_positions:
                    prices = MSRMaker.sample_prices(ev)
                    # and update our offers
                    for (out, (b, s)) in prices.items():
                        out.sell_offer = b  # user can sell at our buy price
                        out.buy_offer = s   # user can buy at our sell price
                        print("b: %f s: %f" % (b, s))
                        out.save()
                # TODO: add shares to the user?

            ord.is_processed = True
            acc.save()
            ord.save()
            logger.debug("Order '%s' processed!" % (ord,))

    def connect(self):
        "Starts listening for orders by connecting to the 'order_placed' signal. "
        order_placed.connect(MSRMaker.on_order_placed)

    def disconnect(self):
        "Disconnects from the 'order_placed' signal and stops listening for new orders. "
        order_placed.disconnect(MSRMaker.on_order_placed)