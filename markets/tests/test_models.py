from django.test import TestCase
from markets.models import *
from markets.tests.test_tools import TestTools

# Create your tests here.
class MarketTestCase(TestCase):

    mkt = None
    set = None
    
    def setUp(self):
        TestTools.setup_vs()
        
        self.mkt = Market.objects.create(description = "TestMarket")

    def test_market_event_count(self):
        self.assertEqual(self.mkt.n_events(), 0)

        e1 = TestTools.create_event(self.mkt, "EventA")
        self.assertEqual(self.mkt.n_events(), 1)

        e2 = TestTools.create_event(self.mkt, "EventB")
        self.assertEqual(self.mkt.n_events(), 2)

        self.assertEqual(e1, Event.objects.get(market=self.mkt, description="EventA"))
        self.assertEqual(e2, Event.objects.get(market=self.mkt, description="EventB"))

    def test_market_dataset_count(self):
        self.mkt = Market.objects.create(description = "TestMarket")
        self.assertEqual(self.mkt.n_datasets(), 0)

        s1 = TestTools.create_dataset(self.mkt, "DataA")
        self.assertEqual(self.mkt.n_datasets(), 1)

        s2 = TestTools.create_dataset(self.mkt, "DataB")
        self.assertEqual(self.mkt.n_datasets(), 2)

        self.assertEqual(s1, DataSet.objects.get(market=self.mkt, description="DataA"))
        self.assertEqual(s2, DataSet.objects.get(market=self.mkt, description="DataB"))
        
class DataSetTestCase(TestCase):

    mkt = None

    def setUp(self):
        TestTools.setup_vs()

        self.mkt = TestTools.create_binary_market()


    def test_set_create_count(self):

        set = DataSet.objects.create(market = self.mkt, description = "TestSet")
        set.save()

        self.assertEqual(set.has_data(), False)
        self.assertEqual(set.datum_count, 0)
        self.assertEqual(set.active_datum_id, 0)
        self.assertEqual(Datum.objects.filter(data_set=set).count(), 0)

        set.random(10)
        self.assertEqual(set.has_data(), True)
        self.assertEqual(set.datum_count, 10)
        self.assertEqual(set.datum_set.count(), 10)

        set.random(10)
        self.assertEqual(set.has_data(), True)
        self.assertEqual(set.datum_count, 20)
        self.assertEqual(set.datum_set.count(), 20)

        set.delete()

    def test_set_challenge_start(self):
        """
        Checks whether challenges start properly. 
        """
        set = TestTools.create_dataset(self.mkt, "TestSet", 10)

        t_start = timezone.now()
        set.start()
        t_end = timezone.now()

        self.assertTrue(set.is_active)
        self.assertEqual(set.active_datum_id, 0)
        self.assertTrue(set.challenge_start >= t_start and set.challenge_start <= t_end)

        

    def test_set_challenge_stop(self):
        """
        Checks whether challenges stop properly. 
        """
        set = TestTools.create_dataset(self.mkt, "TestSet", 10)
        set.start()
        set.stop()
        
        self.assertFalse(set.is_active)

    def test_set_set_datum(self):
        """
        Checks whether setting the correct datum is reflected properly. 
        """

        set = TestTools.create_dataset(self.mkt, "TestSet", 10)
