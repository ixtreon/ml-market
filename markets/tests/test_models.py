from django.test import TestCase
from markets.models import Market, DataSet, Outcome, Event
from markets.tests.test_tools import TestTools

# Create your tests here.
class MarketTestCase(TestCase):

    mkt = None
    set = None
    
    def setUp(self):
        self.mkt = Market.objects.create(description = "TestMarket")

    def test_create_events(self):
        self.assertEqual(self.mkt.n_events(), 0)

        e1 = TestTools.create_event(self.mkt, "EventA")
        self.assertEqual(self.mkt.n_events(), 1)

        e2 = TestTools.create_event(self.mkt, "EventB")
        self.assertEqual(self.mkt.n_events(), 2)

        self.assertEqual(e1, Event.objects.get(market=self.mkt, description="EventA"))
        self.assertEqual(e2, Event.objects.get(market=self.mkt, description="EventB"))

    def test_create_datasets(self):
        self.mkt = Market.objects.create(description = "TestMarket")
        self.assertEqual(self.mkt.n_datasets(), 0)

        s1 = TestTools.create_dataset(self.mkt, "DataA")
        self.assertEqual(self.mkt.n_datasets(), 1)

        s2 = TestTools.create_dataset(self.mkt, "DataB")
        self.assertEqual(self.mkt.n_datasets(), 2)

        self.assertEqual(s1, DataSet.objects.get(market=self.mkt, description="DataA"))
        self.assertEqual(s2, DataSet.objects.get(market=self.mkt, description="DataB"))
        
        