from django.apps import AppConfig
from django import apps
from msr_maker.msrmaker import MSRMaker
from markets.cron import Cron
from order_book.order_book import OrderBook
from markets.models import MarketType
from markets.signals import order_placed
from markets.log import logger

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
        # attach a market maker to this instance. 
        order_placed.connect(self.on_order_placed)

        # Start a Cron instance
        # updates challenges that completed while we dead
        # and schedules challenge updates
        self.cron = Cron()
        self.cron.start()

    @staticmethod
    def on_order_placed(sender, **kwargs):
        "Handles creation of orders by dispatching them to the . "
        # TODO: implement a queue?
        # also: does transaction.atomic() serve as a lock? 

        ord = kwargs['order']
        acc = ord.account
        assert (not ord.is_processed())
        logger.info("Processing order '%s' from user '%s' placed at '%s'. " % 
                    (str(ord), str(acc.user), ord.timestamp))

        market = acc.market
        mkt_type = market.type

        market_handler = MarketConfig.market_types.get(mkt_type)
        logger.info("Sending the order to the '%s' handler. " % 
                    (mkt_type))
        assert (market_handler != None)

        market_handler.order_placed(ord)