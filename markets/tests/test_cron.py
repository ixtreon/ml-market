from django.test import TestCase
from django import db

from markets.tests.test_tools import *
from time import sleep
from threading import Timer
from django.db import transaction

# Create your tests here.
class CronTestCase(TestCase):

    mkt = None
    set = None

    def setUp(self):
        TestTools.setup_vs()
        # create a yes/no market and a random dataset for it
        self.mkt = TestTools.create_binary_market()
        self.set = TestTools.create_dataset(self.mkt)


    def test_cron_works(self):

        # the challenge duration in seconds and time allowed for processing
        set_duration_sec = 3
        set_extra_timeout = 1

        # set the reveal interval and start the set
        self.set.reveal_interval = 1 / 24 / 60 / 60 * set_duration_sec
        self.set.reset()
        self.set.start()
        self.assertEqual(self.set.active_datum_id, 0)
        db.close_old_connections()
        db.close_connection()
        print("Started a challenge to expire in %d seconds. " % set_duration_sec)

        sleep(set_duration_sec + set_extra_timeout)

        self.assertEqual(self.set.active_datum_id, 1)
        #Timer(5 + 5, 
        #      lambda:
        #        ).start()
