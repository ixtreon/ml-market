
from markets.models import AccountBalance, MarketBalance
class MarketMaker(object):
    """Specifies the actions each market maker should implement. """

    def order_placed(self, ord):
        """Handles placing of an order by the user. """
        raise NotImplementedError()
    
    def can_quote(self):
        """Gets whether the market maker provides price quotes. """
        raise NotImplementedError()

    def price_quote(self, ord):
        """Gets a price quote for the given order. """
        raise NotImplementedError()


    def update_prices(self, ev):
        """
        Updates the current price for each of the events' outcomes, as well as the current ask and offer prices for it. 

        This method is called at the start of markets to initialise the market prices. 
        It should be also used by implementing classes after handling both the order_placed and end_challenge events to update the price offers. 
        """
        raise NotImplementedError()
    
    def reset_market(self, mkt):
        """
        Resets the balances of all participants of the given market. Does so by calling self.reset_event for each event in the market. 
        
        To be used by implementing classes. 
        """
        for ev in mkt.events.all():
            self.reset_event(ev)

    def reset_event(self, ev):
        """
        Resets the market and account balances (amount of shares held) for each of this event's outcomes. 

        Calls self.update_prices with the given event 
        """
        AccountBalance.reset(ev)
        MarketBalance.reset(ev)
        self.update_prices(ev)

        
    def end_challenge(self, datum):
        """
        Finalises a challenge given the current datum. 

        Treats the amounts in AccountBalance and MarketBalance as the number of shares owned for each Outcome. 
        Rewards all players holding shares for winning outcomes (i.e. Results) with 1 credit, or substracts money in the case they have negative. 
        
        Iterates through all events in this market, gets the Result of the event, and rewards all players with a non-neutral position in the outcome 
        with 1 credit for each share they possess. Finally, resets the market state. 
        """

        mkt = datum.data_set.market


        for ev in mkt.events.all():
            # get the event result
            try:
                result = Result.objects.get(datum=datum, outcome__event=ev)
            except:
                # if it does not exist, print a warning
                logger.warn("Datum %s from DatSet %s does not define a result for event %s. " 
                            % (datum, datum.dataset, ev))
            else:
                # if it was found, reward the winners (and penalise the losers)
                for accShares in result.outcome.accountbalance_set.all():
                    if accShares.amount != 0:
                        acc = accShares.account
                        acc.funds += accShares.amount
                        acc.save()

                        logger.debug("Rewarded user %s with %d credits. " % (acc.user, accShares.amount))

            # reset all account and market amounts for this event
            self.reset_event(ev)