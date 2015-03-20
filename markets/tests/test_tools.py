
from markets.models import Market, DataSet, Outcome, Event

class TestTools():

    @staticmethod
    def create_binary_market(mkt_name = "TestMarket", event_name = "TestEvent"):
        """Creates a sample market with a single event of two outcomes. """
        
        mkt = Market.objects.create(description=mkt_name)
        event = Event.objects.create(description=event_name, market=mkt)
        outcomeA = Outcome.objects.create(event = event, name = "Outcome A")
        outcomeB = Outcome.objects.create(event = event, name = "Outcome B")
        return mkt

    def create_random_dataset(mkt, set_name = "TestSet", n_items = 10):
        """Creates a randomised dataset for the given market with the specified number of items. """
        set = DataSet.objects.create(market = mkt, description = set_name)
        set.random(n_items)
        return set