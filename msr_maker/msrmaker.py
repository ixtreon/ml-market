
from markets.signals import order_placed
from django.db import transaction
from markets.models import Outcome, Order
from msr_maker.models import Supply
from itertools import groupby
from math import *
from _decimal import Decimal


# The liquidity parameter b. 
b = 100

def log_C(b, supply):
    print("sup: %s" % str(supply))
    return b * log(sum(exp(s / b) for s in supply))

def log_msr_price(cur_supply, new_supply):
    return log_C(b, new_supply) - log_C(b, cur_supply)


class MSRMaker():

    def on_order_placed(sender, **kwargs):
        "Handles creation of orders by processing them instantly. "
        # TODO: what about a queue?
        # also: does transaction.atomic() serve as a lock?
        print("wohoo, made an order!")
        # marketmaker handling
        ord = kwargs['order']
        assert (not ord.is_processed)
        with transaction.atomic():
            print("processing order '%s'" % str(ord))
            # get the unique events we are betting for
            event_positions = MSRMaker.get_ev_pos(ord)
            acc = ord.account
            # for each event get the supplies for it
            supplies = [Supply.for_event(ev) for (ev, ps) in event_positions]
            # for each event get a dict (outcome: supply)
            supply_amounts = [{ s.outcome: s.amount for s in ev_s } for ev_s in supplies ]
            # get the risk for holding these supplies
            current_risk = sum(log_C(b, s.values()) for s in supply_amounts)

            # for each position we have an opinion on
            print(list(event_positions))
            for (i, (ev, ps)) in enumerate(event_positions):
                for p in ps:
                    # get the supplies for it
                    # (same index as in event_pos)
                    # and modify the amount
                    print("b4: %f" % supply_amounts[i][p.outcome] )
                    supply_amounts[i][p.outcome] += p.amount
                    print("b4: %f" % supply_amounts[i][p.outcome] )

            new_risk = sum(log_C(b, s.values()) for s in supply_amounts)

            cost = Decimal(new_risk - current_risk)
            print("the total sum for the order is %f" % (cost))

            ord.is_successful = (acc.funds >= cost)
            if ord.is_successful:
                # deduct credits
                acc.funds -= cost

                # update the amounts
                for (i, (ev, ps)) in enumerate(event_positions):
                    for p in ps:
                        s = Supply.get(p.outcome)
                        s.amount += p.amount
                        s.save()
                        
                        print("%s: %f" % (str(s.outcome), s.amount))

                    for out in ev.outcome_set.all():
                        supply_amounts[i][out] += 1
                        pos_offer = sum(log_C(b, s.values()) for s in supply_amounts) - new_risk
                        supply_amounts[i][out] -= 2
                        neg_offer = new_risk - sum(log_C(b, s.values()) for s in supply_amounts)
                        supply_amounts[i][out] += 1

                        out.sell_offer = pos_offer
                        out.buy_offer = neg_offer
                        print("b: %f s: %f" % (neg_offer, pos_offer))
                        out.save()
                # print em?

            ord.is_processed = True
            acc.save()
            ord.save()
            print("order done")
            # add shares
            # update prices

    def get_ev_pos(ord):
        "Gets all positions in the given order and groups them by their event. "
        ps = list(ord.position_set.all())

        get_ev = lambda p: p.outcome.event
        ps.sort(key=get_ev)
        return [(e,list(p)) for (e,p) in groupby(ps, key=get_ev)]

    def connect(self):
        "Starts listening for orders by connecting to the 'order_placed' signal. "
        order_placed.connect(MSRMaker.on_order_placed)
        print("msr-maker hooked the orders!")


    def get_price(ev, ps):
        "Gets the price for the given positions. "
        # gets the current supplies for ALL outcomes in this event 
        # (even for outcomes not in the supply db yet)
        ev_outs = ev.outcome_set.all()
        cur_risk = log_C(b, ev)
        # atomicity in the parent block makes this safe (hope so)
        for pos in ps:
            s = Supply.get(pos.outcome)
            s.amount += pos.amount
            s.save()

        new_risk = log_C(b, ev)
        return Decimal(new_risk - cur_risk)
