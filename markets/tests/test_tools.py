from markets.models import Market, DataSet, Outcome, Event, Datum
from django import db
from django.db import transaction

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

    @transaction.atomic
    def create_driver_identification():

        mkt = Market.objects.create(
            name="Driver Profile Identification", 
            description="""In this market specific driver profiles are presented in the form of a list of GPS co-ordinates. The goal of the market is the identification of key features in the driving style of the particular drivers. """)
        mkt.save()

        events = [
            "Speeding Level",
            "Overall driver safety",
            "Overall driver safety",
            "Overall driver safety",
            "",
            ]

        for i in range(0, len(events)):
                a = events[i]
                event = Event.objects.create(
                    name='%s' % (a),
                    description='Whaaat' % (a, b),
                    market=mkt)
                event.save()

                eLow = Outcome.objects.create(
                    event = event,
                    name = 'Low %s' % a,
                    description = '%s beats %s with at least one point' % (a,b))
                eLow.save()
                eMid = Outcome.objects.create(
                    event = event,
                    name = "Draw",
                    description = 'The match ends in a draw')
                eMid.save()
                eHigh = Outcome.objects.create(
                    event = event,
                    name = '%s wins' % b,
                    description = '%s beats %s with at least one point' % (b,a))
                eHigh.save()

        set = DataSet.objects.create(
            market=mkt,
            name="Six Nations 1990-1999",
            description="A dataset of 10 randomised Six Nations tournaments, supposedly happening in the years 1990-2000. <br/> These have nothing to do with the real Six Nations results. ")
        set.save()
        for i in range(1990, 2000):
            d = Datum.random(set, "Rugby Tournament %d" % i, "What did or did not happen during the face-off in the year %d. " % i)

        set.start()