from markets.models import Market, DataSet, Outcome, Event

class TestTools():

    @staticmethod
    def setup_vs():
        """
        Sets up the django environment if running the tests from the Visual Studio Test Explorer instead of the command-line. 

        Does nothing if tests are executed from the command-line. 

        See https://pytools.codeplex.com/workitem/1485
        """
        try:
            import django
            django.setup()
        except:
            pass


    @staticmethod
    def create_binary_market(mkt_name = "TestMarket", event_name = "TestEvent"):
        """Creates a sample market with a single event of two outcomes. """
        
        mkt = Market.objects.create(description=mkt_name)

        TestTools.create_event(mkt, n_outcomes=2)

        mkt.save()
        return mkt

    @staticmethod
    def create_event(mkt, event_name = "TestEvent", n_outcomes = 2):
        """Creates a sample event for the specified market. """

        event = Event.objects.create(description=event_name, market=mkt)
        for i in range(n_outcomes):
            out = Outcome.objects.create(event = event, name = "Outcome %d" % i)
            out.save()
        event.save()
        return event

    @staticmethod
    def create_dataset(mkt, set_name = "TestSet", n_items = 10):
        """Creates a randomised dataset for the given market with the specified number of items. """
        set = DataSet.objects.create(market = mkt, description = set_name)
        set.random(n_items)
        set.save()
        return set