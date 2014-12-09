import datetime
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_init
from decimal import Decimal, getcontext
import django
import math
import os
import django.core.exceptions
import random
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from markets.signals import order_placed, dataset_change
from decimal import Context
from datetime import timedelta
from django import forms
from markets.fields.TimedeltaField import TimedeltaField

def to_decimal(f):
    return Decimal(f, Context(prec=2))
def DecimalField():
    return models.DecimalField(default=0, decimal_places=2, max_digits=7)

def t():
    return timezone.now()

class Market(models.Model):
    description = models.CharField(max_length=255, default='Add a description here. ')

    pub_date = models.DateTimeField('Date Started')

    def active_set(self):
        "Gets the active dataset for this market, or None if the market is inactive. "
        try:
            return self.dataset_set.get(market=self, is_active=True)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many active datasets! Invalid state?.. ")

    def n_events(self):
        return Event.objects.filter(market=self).count()

    def n_datasets(self):
        return DataSet.objects.filter(market=self).count()

    def get_user_account(self, u):
        "Gets the user's account for this market, or None if they are not registered. "
        try:
            return u.account_set.get(market=self)
        except Account.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many accounts for this user! Invalid state?.. ")

    def is_active(self):
        return self.active_set() != None
    is_active.boolean = True

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        super(Market, self).save()
    
# contains info about the state of a given market at a given time
# that is the current price, as determined by the processed orders
# and the previous state (including previous prices of course)
class MarketState(models.Model):
    market = models.ForeignKey(Market)
    # previous state
    # current prices
    # list of processed orders
    # timestamp

# represents some user's bank account for a given market. 
# should contain current funds, as well as standing orders
class Account(models.Model):
    user = models.ForeignKey(User)
    market = models.ForeignKey(Market)
    funds = DecimalField()
    
    def standing_orders(self):
        return self.order_set.all()


    @transaction.atomic
    def place_multi_order(self, market, position):
        try:
            order = Order.new_multi(market, self, position)
        except Exception as err:
            raise Exception("failed creating an order: " + str(err))
        
        order_placed.send(sender=self.__class__, order=order)
        return order

class Event(models.Model):
    "A set of outcomes for a market. "
    description = models.CharField(max_length=255, default='Some outcome set')
    market = models.ForeignKey(Market, related_name="events")

    def fix_outcomes(self):
        "Makes sure all outcomes sum to 1"
        # get the outcomes from the market
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

    def __str__(self):
        return "%s (%s)" % (self.description, self.market)

# represents a single outcome in a multiclass market. 
class Outcome(models.Model):
    event = models.ForeignKey(Event, default=1, related_name='outcomes')

    name = models.CharField(max_length=255)

    # TODO: remove
    current_price = DecimalField()

    sell_offer = DecimalField()
    buy_offer = DecimalField()

    def __str__(self):
        return self.name + " : " + str(self.current_price)

class DataSet(models.Model):
    # the market this dataset is for
    market = models.ForeignKey(Market)

    description = models.CharField(max_length=255, default='Add a description here. ')

    # whether the dataset is intended for training
    # currently unused in code
    is_training = models.BooleanField(default=False)

    # whether the data set is active for the given market
    is_active = models.BooleanField(default=False)

    # the count of datums
    # should not be set manually
    datum_count = models.IntegerField(default=0)

    # the id of the active datum
    active_datum_id = models.IntegerField('Active challenge id', default=0)

    # time when the active datum was revealed
    challenge_start = models.DateTimeField('Challenge started', default=datetime.datetime(2014,1,1))
    
    # interval between consecutive challenges in days
    reveal_interval = models.IntegerField('Interval between challenges', default=7)

    def next_challenge_in(self):
        return self.challenge_end() - timezone.now()

    def challenge_end(self):
        return self.challenge_start + datetime.timedelta(days=self.reveal_interval)

    def has_data(self):
        "Gets whether this dataset has any data in it. "
        assert (self.datum_set.count() == 0) == (self.datum_count == 0)
        return self.datum_count == 0

    def has_datum(self, id):
        "Gets whether this DataSet contains a datum with the given id"
        has_it = self.datum_set.filter(id=id).count() > 0
        assert has_it == (id < self.active_datum_id)
        return has_it

    def active_datum(self):
        "Gets the active datum using the active_datum id"
        try:
            return self.datum_set.get(set_id=self.active_datum_id)
        except ObjectDoesNotExist:
            raise Exception("No active challenge!")
        except MultipleObjectsReturned:
            raise Exception("Too many active challenges! Invalid state?.. ")
        
    def get_outcomes(self):
        return self.market.outcomes.all()

    @transaction.atomic
    def start(self):
        "Sets this DataSet as the active set for its market."
        # if there's another active dataset it is made inactive
        ds = self.market.active_set()
        if ds == this:
            return

        if ds != None:
            ds.is_active = False
            ds.save()
        self.is_active = True
        self.challenge_start = timezone.now()
        self.save()

    def pause(self):
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
            raise Exception("No active challenge!")
        self.active_datum_id = 0
        self.challenge_start = timezone.now()
        self.save()

    def next_challenge_id(self):
        new_id = self.active_datum_id + 1
        if not self.has_datum(new_id):
            raise Exception("No next challenge!")
        return new_id

    def next(self):
        """Advances this active set to the next datum (challenge) and raises the set_expire_changed signal.
If there is no datum with such id, the set is made inactive. \
Returns whether the set is active. """
        assert self.is_active
        try:    # try advancing the dataset
            self.active_datum_id = self.next_challenge_id()
            self.challenge_start = timezone.now()
        except: # make it inactive if no next datum
            self.is_active = False
        self.save()
        return self.is_active

    # creates a new datum for this dataset and saves it
    def random_datum(self, x = ""):
        """Creates a new random datum for this DataSet and saves it. 
Generates a random result for each event in the DataSet market. """

        if not x: # generate a placeholder name
            x = self.description + " " + str(self.datum_count)

        dat = Datum(
            x = x,
            set_id = self.datum_count,
            data_set = self)
        dat.save()

        # generate random outcomes for each event
        es = self.market.events.all()
        for e in es:
            o = e.random_outcome()
            r = Result(
                datum=dat,
                outcome=o)
            r.save()


    # generates a new dataset with n_datums data points
    # each specifying a random outcome for each event in this market. 
    # Finally saves the dataset. 
    def new_random(self, n_datums=0):

        if n_datums <= 0:
            raise ValueError("n_datums must be positive!")

        for i in range(n_datums):
            dat = self.random_datum()
            # don't forget to increase the count of data points
            self.datum_count += 1
        self.save()

    # creates a new dataset from a file
    # TODO: add schema as param?
    def new_from_file(market, file):
        pass

    def __str__(self):
        return "dataset #%d" % (self.id)

    def save(self, *args, **kwargs):
        dataset_change.send(self.__class__, set=self)
        #print("event weeee!")
        return super().save(*args, **kwargs)

class Datum(models.Model):
    # the set this data point is part of
    data_set = models.ForeignKey(DataSet)
    # the test data
    x = models.CharField(max_length=1024)

    # the consecutive id of the datum in the set
    set_id = models.IntegerField()

    def __str__(self):
        return "%s'%d" % (self.data_set,self.set_id)

class Result(models.Model):
    "The actual outcome of a given event for the specified datum. "
    datum = models.ForeignKey(Datum)
    outcome = models.ForeignKey(Outcome)
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
    # whether the order is processed
    is_processed = models.BooleanField(default=False)

    is_successful = models.BooleanField(default=False)

    def unprocessed_orders():
        return Order.objects.filter(is_processed=False)

    # gets whether the order is cancelled
    def get_position(self, outcome):
        try:
            return self.position_set.get(outcome=outcome).amount
        except ObjectDoesNotExist:
            return 0
        except MultipleObjectsReturned:
            raise Exception("Too many positions for order %d! Invalid state?.. " % (self.id))
        
    # Gets the order along with a list of the order's position
    # for all the selected outcomes. 
    def get_data(self, outcomes):
        return (self, [self.get_position(out) for out in outcomes])

    # creates a new order for the given account playing on the given market. 
    # looks up the current challenge for that market
    # looks up its current price
    @transaction.atomic
    def new_single(market, account, outcome, amount):
        # get this market's active challenge
        dataset = market.active_set()
        datum = dataset.active_datum()
        # create the order
        order = Order(
            datum = datum,
            account=account,
            timestamp = timezone.now())
        order.save()
        # and its only position
        pos = Position.new(order, outcome, amount)
        pos.save()
        return order

    @transaction.atomic
    def new_multi(market, account, position):
        "Creates a new multi-position order for the given account. "

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
        # and its only position
        for (out, amount) in position:
            pos = Position.new(order, out, amount)
            pos.save()
        return order


    def cancel(self):
        self.delete()
    
# represents a position on a given outcome
# in the context of an order. 
class Position(models.Model):
    "A player's position (opinion) about a given outcome as part of an order. "
    # the order this position
    order = models.ForeignKey(Order)
    # what the claim was
    outcome = models.ForeignKey(Outcome)
    # how much contracts to purchase or sell
    amount = DecimalField()

    # the price the order was processed at. 
    contract_price = DecimalField()

    def new(order, outcome, amount):
        return Position(
            order=order,
            outcome=outcome,
            amount=amount)
    
    # gets the total cost for this position. 
    def get_cost(self, contract_price):
        return self.amount * contract_price

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