from django.apps import AppConfig
from django import apps
from msr_maker.msrmaker import MSRMaker
from markets.cron import Cron

class MarketConfig(AppConfig):
    name = 'markets'
    verbose_name = "ML Markets"

    market_maker = None


    def ready(self):

        # attach a market maker to this instance. 
        self.market_maker = MSRMaker()
        self.market_maker.connect()
        # Start a Cron instance
        # updates challenges that completed while we dead
        # and schedules challenge updates
        self.cron = Cron()
        self.cron.start()