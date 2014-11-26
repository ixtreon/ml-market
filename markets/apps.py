from django.apps import AppConfig
from django import apps
from msr_maker.msrmaker import MSRMaker

class MarketConfig(AppConfig):
    name = 'markets'
    verbose_name = "ML Markets"

    market_maker = None

    def ready(self):
        pass

        # attach a market maker to this instance. 
        self.market_maker = MSRMaker()
        self.market_maker.connect()


        # update challenges that completed while we dead
        # schedule challenge update times