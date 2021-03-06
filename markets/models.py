import datetime
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User

from decimal import Decimal
import os
import random
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from markets.signals import order_placed, dataset_change, dataset_expired
import time
from markets.log import logger
from enum import Enum
from enumfields.fields import EnumIntegerField
from _datetime import timedelta
import itertools
from itertools import groupby
import json

## Decimal handling
decimal_places = 2
def to_decimal(f):
    return Decimal(f).quantize(Decimal(10) ** -decimal_places)
def CurrencyField():
    return models.DecimalField(default=0, decimal_places=decimal_places, max_digits=7)


def t():
    return timezone.now()

class MarketType(Enum):
    """
    The different types of markets with regard to the market maker that is used. 
    """
    order_book = 1
    parimutuel = 2
    msr_maker = 3

    def str(ty):
        if ty == MarketType.order_book:
            return "Order Book"
        elif ty == MarketType.parimutuel:
            return "Parimutuel"
        elif ty == MarketType.msr_maker:
            return "MSR Maker"
        return str(ty)

class Interval():
    """

    """
    Years = lambda dt: dt.year
    Months = lambda dt: Interval.Years(dt) * 12 + dt.month
    Days = lambda dt: Interval.Months(dt) * 31 + dt.day
    Hours = lambda dt: Interval.Days(dt) * 24 + dt.hour
    Minutes = lambda dt: Interval.Hours(dt) * 60 + dt.month
    Seconds = lambda dt: Interval.Minutes(dt) * 60 + dt.month


class Market(models.Model):
    name = models.CharField(max_length=255, default='Market name here. ')
    description = models.CharField(max_length=1024, default='Market description here. ')

    pub_date = models.DateTimeField('Date Published')

    type = EnumIntegerField(MarketType, default=MarketType.msr_maker)

    def type_string(self):
        return MarketType.str(self.type)

    def challenge_end(self):
        if self.is_active():
            return self.active_set().challenge_end()
        else:
            return None
        
    def challenge_end_ticks(self):
        """
        Gets the challenge_end datetime in the form of ticks elapsed since the Epoch. 
        """
        t = self.challenge_end()
        if t:
            return int(time.mktime(t.timetuple()) * 1000)
        else:
            return None

    def challenge_start_ticks(self):
        """
        Gets the challenge_start datetime in the form of ticks elapsed since the Epoch. 
        """
        t = self.challenge_start()
        if t:
            return int(time.mktime(t.timetuple()) * 1000)
        else:
            return None

    def challenge_start(self):
        if self.is_active():
            return self.active_set().challenge_start
        else:
            return None

    def active_set(self):
        "Gets the active dataset for this market, or None if the market is inactive. "
        try:
            return self.dataset_set.get(market=self, is_active=True)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many active datasets! Invalid state?.. ")

    def active_datum(self):
        set = self.active_set()
        if not set:
            return None
        return set.active_datum()

    def n_events(self):
        "Gets the total amount of events registered with this market. "
        return Event.objects.filter(market=self).count()

    def n_datasets(self):
        "Gets the total number of datasets for this market. "
        return DataSet.objects.filter(market=self).count()

    def primary_account(self, u):
        "Returns the user's primary account for this market, or None if they are not registered. "
        if u.is_anonymous():
            return None

        try:
            return u.account_set.get(market=self, is_primary=True)
        except Account.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many accounts for this user! Invalid state?.. ")

    def create_primary_account(self, u):
        "Creates a primary account for the given user. Throws an exception if the account exists. "
        assert not self.primary_account(u)
        a = Account(user=u, market=self, is_primary=True, funds=100)
        a.save()
        return a

    def api_accounts(self, u):
        "Gets all API accounts created by the given user for this market. "
        return u.account_set.filter(is_primary=False)

    def is_active(self):
        "Gets whether this market has an active dataset. "
        return self.active_set() != None
    is_active.boolean = True    # show it as an icon in the admin panel


    def parse_bid(self, post):
        """
        Parses the data from the given POST request. 
        Returns a list of tuples containing the amount wagered on each outcome for this market. 
        """
        pos = []
        outcomes = Outcome.objects.filter(event__market=self)

        for out in outcomes:
            try:
                ord_pos = int(post["pos_%i" % (out.id)])
            except:
                ord_pos = 0

            if ord_pos != 0:
                pos.append((out, ord_pos))
        return pos

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Sets the pub_date field the first time the object is saved
        if self.pub_date == None:
            self.pub_date = timezone.now()
            

        super(Market, self).save()

class Account(models.Model):
    """
    Represents a user's bank account for a given market. 
    Normal users are allowed only a primary account 
    while admin users can create multiple secondary accounts. 
    """

    user = models.ForeignKey(User)
    
    market = models.ForeignKey(Market)
    
    funds = CurrencyField()

    is_primary = models.BooleanField(default=False)
    
    def all_orders(self):
        return self.order_set.all()

    @transaction.atomic
    def place_order(self, market, position):
        """
        Tries to place an order from this account on the given market with the given positions. 
        Each position is a tuple of an outcome, and the amount to wager on that outcome. 

        Returns None if the position list is empty. 
        """

        if not position:
            return None

        try:
            order = Order.new(market, self, position)
        except Exception as err:
            raise Exception("failed creating an order: " + str(err))

        assert (not order.is_processed())
        assert (not order.is_successful)

        # sends the order_placed signal. 
        order_placed.send(sender=self.__class__, order=order)
        return order

class Event(models.Model):
    "A set of outcomes for a market. "
    name = models.CharField(max_length=255, default='Event name here. ')
    description = models.CharField(max_length=1024, default='Event description here. ')
    market = models.ForeignKey(Market, related_name="events")

    def normalise_outcomes(self):
        "Makes sure all outcomes sum to 1"
        # unused
        outcomes = list(self.outcomes.all())
        
        pdf_invalid = (self.outcomes.filter(current_price=0).count() > 0)

        if pdf_invalid:
            n_outcomes = len(outcomes)
            for o in self.outcomes.all():
                o.current_price = 1 / n_outcomes
                o.save()
        else:
            pdf_total = sum(o.current_price for o in outcomes)
            pdf_left = Decimal(1)   # make sure we never distribute more than 1
            for o in outcomes:
                new_price = o.current_price / pdf_total
                o.current_price = min(pdf_left, new_price)
                pdf_left -= o.current_price
                # still possible to get a 0 here
                o.save()

    def random_outcome(self):
        "Draws a random outcome from this set. "
        outcomes = list(self.outcomes.all())
        n_outcomes = len(outcomes)
        random_outcome_id = random.randint(0, n_outcomes-1)   # range is inclusive at both ends
        return outcomes[random_outcome_id]

    def price_histogram(self, dt_from, dt_to):
        "Gets the price histogram for the event in the given time interval. """
        d = dt_from - dt_to
        pass

    def activity_histogram(self, dt_from, dt_to, interval):
        """Gets the amount of trades that occured in the given time interval."""
        d = dt_from - dt_to
        # get the list of positions in the given interval
        trades = Position.objects.filter(outcome__event=self)
        trades = trades.filter(order__timestamp__gte=dt_from)
        trades = trades.filter(order__timestamp__lte = dt_to)
        trades = list(trades)
        trades.sort(key=lambda p: p.order.timestamp)


        first_bin = interval(dt_from)
        last_bin = interval(dt_to)
        n_bins = last_bin - first_bin + 1
        bins = []
        i = 0
        for bin_id in range(first_bin, last_bin + 1):
            counts = 0
            while i < len(trades) and interval(trades[i].order.timestamp) == bin_id:
                counts += 1
                i += 1
            bins.append(counts)
        return bins

    def get_prices(self):
        return [(o.buy_offer, o.sell_offer) for o in self.outcomes.all()]

    def json_prices(self):
        return json.dumps([ (o.name, int(100 * o.current_price)) for o in self.outcomes.all()])

    def __str__(self):
        return self.name

# represents a single outcome in a multiclass market. 
class Outcome(models.Model):
    event = models.ForeignKey(Event, default=1, related_name='outcomes')
        
    name = models.CharField(max_length=255)

    description = models.CharField(max_length=1024, default='Outcome description here. ')


    # TODO: remove
    current_price = CurrencyField()

    sell_offer = CurrencyField()
    buy_offer = CurrencyField()

    def market_balance(self):
        return MarketBalance.get(self).amount

    def price_tooltip(self):
        return "You can buy a single share for %.2f.\nYou can sell a single share for %.2f. " % (self.buy_offer, -self.sell_offer)

    def __str__(self):
        return self.name + " : " + str(self.current_price)

class DataSet(models.Model):
    # the market this dataset is for
    market = models.ForeignKey(Market)

    name = models.CharField(max_length=255, default='DataSet name here. ')

    description = models.CharField(max_length=1024, default='DataSet description here. ')

    # whether the dataset is intended for training
    # currently unused in code
    is_training = models.BooleanField(default=False)

    # whether the data set is active for the given markte
    is_active = models.BooleanField(default=False)

    # the count of datums
    # should not be set manually
    datum_count = models.IntegerField(default=0)

    # the id of the active datum
    active_datum_id = models.IntegerField('Active challenge id', default=0)
    
    # time when the active datum was revealed
    challenge_start = models.DateTimeField('Challenge started', default=timezone.datetime(2014,1,1))
    
    # interval between consecutive challenges in days
    reveal_interval = models.FloatField('Interval between challenges', default=7)


    def get_datum(self, set_id):
        "Gets the datum with the specified set_id. Throws an exception if it does not exist. "
        return self.datum_set.get(set_id=set_id)

    def next_id(self):
        """
        Retrieves an id for the next datum and advances self.datum_count. 
        """
        id = self.datum_count
        self.datum_count += 1
        self.save()
        return id

    def next_challenge_in(self):
        """
        Gets the time remaining until this challenge ends as a string. 
        """
        if self.is_active:
            return self.challenge_end() - timezone.now()
        return "N/A"

    def challenge_duration(self):
        """
        Gets a timedelta representation of the duration of a challenge. 
        """
        return datetime.timedelta(days=self.reveal_interval)

    def challenge_end(self):
        """
        Gets the DateTime the active challenge ends at. 

        If this challenge has a negative duration, it is assumed to continue indefinitely. 
        """
        if self.reveal_interval < 0:
            return datetime.datetime.max
        return self.challenge_start + self.challenge_duration()

    def challenge_expired(self):
        """
        Gets whether this set's current challenge has expired.
        """
        return self.challenge_end() < timezone.now()

    def force_advance(self):
        """
        Forces the finalisation of this dataset's current challenge and start the new one. 
        """
        self.challenge_start = timezone.now() - self.challenge_duration()
        self.save()

    def has_data(self):
        """
        Gets whether this dataset has any datums. 
        """
        assert self.datum_set.count() == self.datum_count
        assert self.datum_count >= 0

        return self.datum_count > 0

    def has_datum(self, id):
        """
        Gets whether this DataSet contains a datum with the given id. 
        """
        try:
            d = self.get_datum(id)
        except ObjectDoesNotExist:
            assert (id >= self.datum_count)
            return False
        assert (id < self.datum_count)
        return True

    def active_datum(self):
        """
        Gets the active datum. Throws an exception if it does not exist. 
        """
        return self.get_datum(self.active_datum_id)

    def get_outcomes(self):
        """
        Gets all outcomes defined for this market. 
        """
        return self.market.outcomes.all()

    @transaction.atomic
    def start(self):
        "Sets this DataSet as the active set for its market."
        # if there's another active dataset it is made inactive
        ds = self.market.active_set()
        if ds == self:
            return

        if not self.has_data():
            raise Exception("Unable to start a set with no datums. ")

        if ds != None:
            ds.is_active = False
            ds.save()

        self.is_active = True
        self.challenge_start = timezone.now()
        self.save()

    def stop(self):
        self.is_active = False
        self.save()

    def set_challenge(self, i):
        "Sets the next challenge. "
        if not self.has_datum(i):
            raise Exception("No challenge with id %d for set %s!" % (i, self))

        self.active_datum_id = i
        self.challenge_start = timezone.now()

        self.save()


    def reset(self):
        "Resets active_datum_id to 0. If there is no datum with id of 0, an exception is thrown. "
        if not self.has_data():
            raise Exception("Unable to reset a set with no data! ")

        assert self.has_datum(0)
        self.active_datum_id = 0
        self.challenge_start = timezone.now()
        self.save()

    def next_challenge_id(self):
        """
        Gets the id of the next challenge (datum). 
        Throws an exception if there is no such datum. 
        """
        new_id = self.active_datum_id + 1

        if not self.has_datum(new_id):
            raise Exception("No next challenge!")

        return new_id



    def next(self):
        """
        Advances this active set to the next datum (challenge) _once_, and raises the dataset_expired signal.
        If there is no datum with such id, the set is made inactive. 
        Returns whether the set is active. 
        """
        assert self.is_active

        # Continue only if there is data in the set
        # should not typically arrive here
        if not self.has_data():
            logger.info("Abruptly ended empty dataset %s (no challenges whatsoever). " % (self.active_datum_id, str(self)))
            self.stop()
            return
        

        # get the current challenge
        try:
            old_datum = self.active_datum()
        except ObjectDoesNotExist:  # log an error and deactive the set
            self.stop()
            logger.error("Unable to find the active data point with id: %d. Stopping the set. " % (self.active_datum_id))
            return
        except MultipleObjectsReturned:
            raise Exception("Too many points with id: %d! Invalid state?.. " % (self.id))
        
        # see if we actually need to advance to the next challenge. 
        if not self.challenge_expired():
            return

        # raise the dataset_expired signal
        dataset_expired.send(self.__class__, datum=old_datum)

        # grab the next challenge (datum)
        try:
            self.active_datum_id = self.next_challenge_id()
        except: # make it inactive if no next datum (this was the last)
            self.is_active = False
            logger.info("Ended challenge #%d for dataset %s (no next challenge). " % (self.active_datum_id, str(self)))
            self.save()
            return
        
        self.challenge_start = self.challenge_end()
        logger.info("Started next challenge #%d for dataset %s. Ends at %s" % (self.active_datum_id, str(self), self.challenge_end()))

        self.save()
        return self.is_active


    def random(self, n_data=10):
        """
        Generates some random datums for this dataset. 
        """
        if n_data <= 0:
            raise ValueError("n_datums must be positive!")

        for i in range(n_data):
            dat = Datum.random(self)
        self.save()

    # creates a new dataset from a file
    # TODO: add schema as param?
    def from_file(market, file):
        pass

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        val = super().save(*args, **kwargs)
        dataset_change.send(self.__class__, set=self)
        return val

class Datum(models.Model):
    """
    Represents an observation in the prediction market. 
    
    Defines a result for each event that was observed in this instance, along with a description specific to the observation. 
    """
    # the set this data point is part of
    data_set = models.ForeignKey(DataSet)

    # the test name
    name = models.CharField(max_length=255, default="Datum name here")

    # the test description
    description = models.CharField(max_length=1024, default="Datum description here")

    # the consecutive id of the datum in the set
    set_id = models.IntegerField()

    @staticmethod
    def random(set, name = "", description = ""):
        """
        Creates a new datum with random results 
        for the outcomes of this DataSet, and then saves it
        """

        id = set.next_id()

        if not name: # generate a placeholder name
            name = "%s %s" % (set.description, id)

        dat = Datum(
            name = name,
            description = description,
            set_id = id,
            data_set = set)
        dat.save()

        # generate random outcomes for each event
        es = set.market.events.all()
        for e in es:
            o = e.random_outcome()
            r = Result(
                datum=dat,
                outcome=o)
            r.save()

        return dat

    def is_valid(self):
        "Checks whether this datum contains results for all market events. "
        market = self.data_set.market
        mkt_events = set(market.events.all())
        for result in self.result_set.select_related('outcome__event'):
            ev = result.outcome.event
            if ev not in mkt_events:
                return False
        return True


    def __str__(self):
        return "%s'%d" % (self.data_set,self.set_id)

class Result(models.Model):
    "The actual outcome of a given event for the specified datum. "
    datum = models.ForeignKey(Datum)
    outcome = models.ForeignKey(Outcome)

    def event(self):
        return self.outcome.event

    def __str__(self):
        return "(%s) wins %s" % (self.outcome, self.datum)

class Order(models.Model):
    """A pending or already processed order from a user for some market"""

    # the account that made the order
    account = models.ForeignKey(Account)
    # for which dataset entry (datum) was the bet made
    datum = models.ForeignKey(Datum)
    # when was the order made
    timestamp = models.DateTimeField('Time created')

    # whether the order was completed successfully
    is_successful = models.BooleanField(default=False)

    @staticmethod
    def reset(ev):
        """
        Cancels all orders for the given event. 
        """
        for ord in Position.objects.filter(outcome__event=ev, is_processed=False):
            ord.cancel()

    def set_processed(self):
        """Marks all positions in this order as processed. """
        for o in self.position_set.all():
            o.is_processed = True
            o.save()

    def is_processed(self):
        """Returns whether all positions in this order are processed. """
        return not self.position_set.filter(is_processed=False).exists()

    def unprocessed_orders():
        "Retrieves all unprocessed orders from the database. "
        return Order.objects.filter(position__is_processed=False)

    def get_position(self, outcome):
        "Gets this order's position for the specified outcome. "
        try:
            return self.position_set.get(outcome=outcome).amount
        except ObjectDoesNotExist:
            return 0
        except MultipleObjectsReturned:
            raise Exception("Too many positions for order %d! Invalid state?.. " % (self.id))
        
    # Gets the order along with a list of the order's positions
    # for all selected outcomes. 
    def get_data(self, outcomes):
        return (self, [self.get_position(out) for out in outcomes])

    def group_by_event(self):
        """
        Groups all positions in this order by their event.
        Returns a dictionary of the events with the list of positions on them as the value. 
        """
        all_ps = list(self.position_set.all())

        get_ev_id = lambda p: p.outcome.event.id
        all_ps.sort(key=get_ev_id)
        return [(ev,list(ps)) for (ev,ps) in groupby(all_ps, key=lambda p: p.outcome.event)]

    # creates a new order for the given account playing on the given market. 
    @staticmethod
    @transaction.atomic
    def new_single(market, account, outcome, amount):
        return Order.new(market, account, [(outcome,amount)]) 

    @staticmethod
    @transaction.atomic
    def new(market, account, positions):
        """
        Creates a new order for the specified market by the given account, specifying the provided positions. 
        """

        # get this market's active challenge
        dataset = market.active_set()
        if not dataset:
            # non-active markets should not be listed
            raise Exception("No active dataset for this market!")

        datum = dataset.active_datum()
        # create the order
        order = Order(
            datum = datum,
            account=account,
            timestamp = timezone.now())
        order.save()

        # and its position
        for (out, amount) in positions:
            pos = Position.new(order, out, amount)
            pos.save()
        return order

    def market(self):
        assert (self.account.market == self.datum.data_set.market)
        return self.account.market

    @transaction.atomic
    def cancel(self):
        self.set_processed()
        self.is_successful = False
        self.save()
    
# represents a position on a given outcome
# in the context of an order. 
class Position(models.Model):
    "A player's position (opinion) about a given outcome as part of an order. "
    # the order this position
    order = models.ForeignKey(Order)
    # what the claim was
    outcome = models.ForeignKey(Outcome)
    # how much contracts to trade
    amount = CurrencyField()

    # whether the position is processed
    is_processed = models.BooleanField(default=False)

    # The price per contract for this position. 
    # Either set by the market maker when it processes the order
    # Or set by the account holder when using an Order Book
    contract_price = CurrencyField()

    def new(order, outcome, amount):
        return Position(
            order=order,
            outcome=outcome,
            amount=amount)
    
    def split(self, amount, price):
        """
        Resolves a part of this position. 
        
        Returns the newly created order which partially completes the solution, or None if the position was fulfilled. """

        assert amount != 0
        assert (amount > 0) ^ (self.amount < 0)
        assert (self.price > price) ^ (self.amount < 0)

        parent_order = self.order
        sum = amount * price

        # modify the funds
        acc = self.order.account
        acc.funds 
        # and the account balance

        if amount == self.amount:
            self.is_processed = True
            self.save()
            return None
        else:
            # remove the amount from this position
            self.amount -= amount
            self.save()

            # create a new, completed dummy order with the same stats as this one
            new_order = Order(account=parent_order.account, datum=parent_order.datum, timestamp=parent_order.timestamp, is_successful = True)
            new_order.save()

            # add the amount
            new_pos = Position(
                order=new_order,
                outcome=self.outcome,
                amount = amount,
                contract_price = price,
                is_processed=True)
            new_pos.save()

            return new_order

    def partial_complete(pa, pb):
        """
        Attempts to partially complete the given two positions. 
        
        In order to do so the positions must be of opposite type, compatible prices and on the same outcome. 

        The price at which the deal is completed is taken as the average of each player's suggested price. 

        The amount of shares exchanged depends on the amounts defined by each position. 
        In case one of the positions can be completed only partially, the amount of traded shares are subtracted from it
        and the trade is completed by creating a new Order which contains the fulfilled part of the transaction. 
        """
        # make sure a sells, b buys
        if pa.amount > 0:
            pa, pb = pb, pa

        assert pb.amount > 0
        assert pa.outcome == pb.outcome
        assert (pb.contract_price >= pa.amount)

        # get the contract price at which the deal is made
        # if the prices differ, takes their average
        if pb.contract_price != pa.contract_price:
            price = (pb.contract_price + pa.contract_price) / 2
        else:
            price = pa.contract_price

        # get the amount and total sum for the current deal
        amount = min(-pa.amount, pb.amount)
        total_sum = price * amount
        
        # modify the accounts' funds
        a_acc = pa.order.account
        a_acc.funds += total_sum
        a_acc.save()
        
        b_acc = pb.order.account
        b_acc.funds -= total_sum
        b_acc.save()

        # modify the account balances
        a_balance = AccountBalance.get(a_acc, self.outcome)
        a_balance.amount -= amount

        b_balance = AccountBalance.get(b_acc, self.outcome)
        b_balance.amount -= amount

        # make sure partial orders are properly processed
        if amount == pb.amount:
            # the buyer's position was processed
            pb.is_processed = True
            pb.save()

            # split position a
            pa.split(amount, price)
        else:
            # the seller's position was processed
            pa.is_processed = True
            pa.save()

            # split position b
            pb.split(amount, price)
        return amount

    # gets the total cost for this position. 
    def get_cost(self):
        return self.amount * self.price

    def __str__(self):
        return "%d tokens for %s" % (self.amount, self.outcome)

# contains uploaded documents to be used as dataset sources. 
class Document(models.Model):
    "A document uploaded by the user to be potentially used as a dataset source. "
    user = models.ForeignKey(User)
    file = models.FileField(upload_to='uploads')
    
    def fileName(self):
        return os.path.basename(self.file.name)

    def exists(self):
        return os.path.isfile(self.file.name)

    # removes non-existant files
    def clean_db_records(u):
        docs = Document.objects.filter(user=u)
        for d in docs:
            if not d.exists():
                d.delete()

    def __str__(self):
        return self.fileName()

class AccountBalance(models.Model):
    """
    Represents the current holdings of an account for a given outcome (variable). 

    Contains the amount of shares held by present by the account owner. 
    """
    account = models.ForeignKey(Account)
    outcome = models.ForeignKey(Outcome)
    amount = CurrencyField()

    @staticmethod
    def get(acc, outcome):
        "Gets or creates the supply for the given account. "
        try:
            supply = outcome.accountbalance_set.get(account=acc)
        except models.ObjectDoesNotExist:
            supply = AccountBalance(account=acc, outcome=outcome)
            supply.save()
        except MultipleObjectsReturned:
            raise Exception("Too many supplies for account '%s'! Invalid state?.. " % (acc))
        return supply

    def get_all(outcome):
        pass
    
    @staticmethod
    def reset(ev):
        """
        Resets the account balances for all players and outcomes in the given event. 
        """
        for out in ev.outcomes.all():
            for acc in out.accountbalance_set.all():
                
                acc.amount = 0
                acc.save()


    @staticmethod
    @transaction.atomic
    def accept_order(order):
        acc = order.account
        for pos in order.position_set.all():
            supply = AccountBalance.get(acc, pos.outcome)
            supply.amount += pos.amount
            supply.save()

            
class MarketBalance(models.Model):
    """
    The current market supply for a given outcome. 
    """
    outcome = models.OneToOneField(Outcome)
    amount = CurrencyField()

    @staticmethod
    def get(outcome):
        "Gets or creates the supply for the given outcome. "
        try:    # try to fetch an existing supply instance
            supply = outcome.marketbalance
        except models.ObjectDoesNotExist:
            supply = MarketBalance(outcome=outcome)
            supply.save()
        except MultipleObjectsReturned:
            raise Exception("Too many supplies for a single outcome! Invalid state?.. ")
        return supply

    @staticmethod
    def for_event(ev):
        "Gets the market maker supplies for all outcomes in the given event. "
        return { out: MarketBalance.get(out).amount for out in ev.outcomes.all() }

    @staticmethod
    def reset(ev):
        """
        Resets the market maker's balance for all outcomes in the given event. 
        """
        for out in ev.outcomes.all():
            try:
                supply = out.marketbalance
            except:
                pass
            else:
                supply.amount = 0
                supply.save()

    @staticmethod
    @transaction.atomic
    def accept_order(order):
        """Adds the amounts from the given order to the market supply. """
        acc = order.account
        for pos in order.position_set.all():
            supply = MarketBalance.get(pos.outcome)
            supply.amount += pos.amount
            supply.save()