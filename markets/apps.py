from django.apps import AppConfig
from django import apps
from msr_maker.msrmaker import MSRMaker
from markets.cron import Cron
from order_book.order_book import OrderBook
from markets.models import MarketType, Event, Interval
from markets.signals import *
from markets.log import logger
from datetime import datetime

class MarketConfig(AppConfig):
    name = 'markets'
    verbose_name = "ML Markets"
    
    msr_maker = MSRMaker()
    order_book = OrderBook()

    market_types = {
        MarketType.msr_maker: msr_maker,
        MarketType.order_book: order_book,
        }

    def ready(self):

        # respond to user, market events
        order_placed.connect(self.on_order_placed)
        dataset_expired.connect(self.on_dataset_expired)


        # Start the Cron instance
        # updates completed challenges
        # schedules and executes new challenges
        self.cron = Cron()
        self.cron.start()

    @staticmethod
    def on_dataset_expired(sender, **kwargs):
        """Handles challenge (datum) expirations in the markets 
        and sends them to the market's maker. """

        datum = kwargs['datum']
        mkt_type = datum.data_set.market.type
        logger.info("Finalising challenge '%s' that ended at '%s' using the '%s' maker. " % 
                    (str(datum), datum.data_set.challenge_end(), mkt_type))
        #market_handler = MarketConfig.market_types.get(mkt_type)
        #market_handler.end_challenge(datum)

    @staticmethod
    def on_order_placed(sender, **kwargs):
        "Handles creation of orders by dispatching them to the appropriate market maker. "

        ord = kwargs['order']
        acc = ord.account
        market = acc.market
        mkt_type = market.type
        market_handler = MarketConfig.market_types.get(mkt_type)

        assert (not ord.is_processed())
        assert (market_handler != None)

        logger.info("Sending order '%s' from user '%s' placed at '%s' to the '%s' handler. " % 
                    (str(ord), str(acc.user), ord.timestamp, mkt_type))
        market_handler.order_placed(ord)