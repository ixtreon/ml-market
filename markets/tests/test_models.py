from django.test import TestCase
from markets.models import Market, DataSet, Outcome, Event

# Create your tests here.
class MarketTestCase(TestCase):

    mkt = None
    set = None
