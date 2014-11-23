from django.apps import AppConfig
from django import apps
from msr_maker.msrmaker import MSRMaker

class MarketConfig(AppConfig):
    name = 'markets'
    verbose_name = "ML Markets"

    market_maker = None

    def ready(self):
        pass
        #MyModel = self.get_model('MyModel')
        
        self.market_maker = MSRMaker()

        self.market_maker.connect()