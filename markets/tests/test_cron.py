from django.test import TestCase
from markets.tests.test_tools import *
from time import sleep
from threading import Timer

# Create your tests here.
class CronTestCase(TestCase):

    mkt = None
    set = None

    def setUp(self):
        self.mkt = TestTools.create_binary_market()

        # create a randomised dataset
        self.set = TestTools.create_dataset(self.mkt)


    def test_cron_works(self):

        # the challenge duration in seconds and time allowed for cleanup
        set_duration_sec = 1
        set_extra_timeout = 333

        # set the reveal interval and start the set
        self.set.reveal_interval = 1 / 24 / 60 / 60 * set_duration_sec
        self.set.reset()
        self.set.start()
        self.assertEqual(self.set.active_datum_id, 0)
        print("Started a challenge to expire in %d seconds. " % set_duration_sec)

        sleep(100)
        #Timer(5 + 5, 
        #      lambda:
        #        self.assertEqual(self.set.active_datum_id, 1)).start()
