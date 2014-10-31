import datetime
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from _decimal import Decimal
import django
import math
import os
import django.core.exceptions
import random
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

def DecimalField():
    return models.DecimalField(default=0, decimal_places=2, max_digits=7)

def t():
    return timezone.now()

class Market(models.Model):
    description = models.CharField(max_length=255, default='Add a description here. ')

    pub_date = models.DateTimeField('Date Started')


    # gets the active dataset for this market, 
    # if no active dataset, returns None. 
    def active_set(self):
        try:
            return self.dataset_set.get(market=self, is_active=True)
        except ObjectDoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many active datasets! Invalid state?.. ")

    # gets the account instance of this user for this market
    # or None if the user has no account. 
    def get_user_account(self, u):
        try:
            return u.account_set.get(market=self)
        except Account.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            raise Exception("Too many accounts for this user! Invalid state?.. ")

    def __str__(self):
        return self.description

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=3)

    # does sum to 1 for prices
    def fix_outcomes(sender, **kwargs):
        # get the outcomes from the market
        market = kwargs['instance']
        outcomes = list(market.outcome_set.all())
        print('cleanup model %s' % (outcomes))
        
        pdf_total = Decimal(0)
        pdf_invalid = False

        invalid = market.outcome_set.all() .filter(current_price=0)

        for o in outcomes:
            if o.current_price == 0:
                pdf_invalid = True
                break
            pdf_total += o.current_price

        if pdf_invalid:
            n_outcomes = len(outcomes)
            for o in Outcome.objects.filter(market=market):
                o.current_price = 1 / n_outcomes
                o.save()
        else:
            pdf_left = Decimal(1)
            for o in outcomes:
                new_price = o.current_price / pdf_total
                o.current_price = min(pdf_left, new_price)
                pdf_left -= o.current_price
                o.save()


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
    def place_single_order(self, market, outcome, amount):
        try:
            order = Order.new_single(market, self, outcome, amount)
        except Exception as err:
            raise Exception("failed creating an order: " + str(err))
        
        print("wohoo, made an order!")
        return order

    @transaction.atomic
    def place_multi_order(self, market, position):
        try:
            order = Order.new_multi(market, self, position)
        except Exception as err:
            raise Exception("failed creating an order: " + str(err))
        
        print("wohoo, made an order!")
        return order


# represents an outcome in a multiclass market. 
class Outcome(models.Model):
    market = models.ForeignKey(Market)

    name = models.CharField(max_length=255)
    current_price = DecimalField()

    def __str__(self):
        return self.name + " : " + str(self.current_price)

class DataSet(models.Model):
    # the market this dataset is for
    market = models.ForeignKey(Market)
    description = models.CharField(max_length=255, default='Add a description here. ')
    # whether the dataset is intended for training
    # currently unused in code
    is_training = models.BooleanField(default=False)
    # whether the data set is active
    # for the given market
    is_active = models.BooleanField(default=False)
    # the count of datums
    # should not be set manually
    datum_count = models.IntegerField(default=0)
    # interval between consecutive challenges in days
    reveal_interval = models.IntegerField('Interval between challenges', default=7)
    # the id of the active datum
    active_datum_id = models.IntegerField(default=0)
    # time when the active datum was revealed
    active_datum_start = models.DateTimeField('Date last challenge was started', default=datetime.datetime.now())

    # gets whether this dataset has any data in it
    def has_data(self):
        assert (self.datum_set.count() == 0) == (self.datum_count == 0)
        return self.datum_count == 0

    # gets whether there's a datum with this id. 
    def has_datum(self, id):
        has_it = self.datum_set.filter(id=id).count() > 0
        assert has_it == (id < self.active_datum_id)
        return has_it

    def active_datum(self):
        try:
            return self.datum_set.get(set_id=self.active_datum_id)
        except ObjectDoesNotExist:
            raise Exception("No active challenge!")
        except MultipleObjectsReturned:
            raise Exception("Too many active challenges! Invalid state?.. ")
        
    def get_outcomes(self):
        return self.market.outcome_set.all()

    # sets itself as the active dataset
    # if there's another active dataset it is made inactive
    @transaction.atomic
    def start(self):
        ds = self.market.active_set()
        if ds != None:
            ds.is_active = False
            ds.save()
        self.is_active = True
        self.active_datum_start = timezone.now()
        self.save()

    # sets self.active_datum_id = 0
    # if no data, throw an exception
    def reset(self):
        if not self.has_data():
            raise Exception("No active challenge!")
        self.active_datum_id = 0
        self.save()

    # should set active_datum_id to the next one
    # if non-existing (corrupted db or last challenge) throw an exception
    def next_challenge(self):
        new_datum = self.active_datum_id + 1
        if not self.has_datum(new_datum):
            raise Exception("No next challenge!")
        self.active_datum_id = new_datum
        self.active_datum_start = timezone.now()
        self.save()

    # creates a new datum for this dataset and saves it
    def add_datum(self, x = "", y = None):
        if y == None:
            # generate a random outcome
            outcomes = list(self.get_outcomes())
            n_outcomes = len(outcomes)
            random_outcome_id = random.randint(0, n_outcomes-1)   # range is inclusive at both ends
            y = outcomes[random_outcome_id]
            print("Generated datum #%d with a random outcome: '%s'" % (self.datum_count, y))
        # TODO: check y is a member

        if x == "":
            # generate a placeholder name
            x = self.market.description + " " + str(self.datum_count)

        dat = Datum(
            x = x,
            y = y,
            set_id = self.datum_count,
            data_set = self)
        dat.save()

    # generates a new dataset with n_datums data points
    # randomly chosen from all the market outcomes
    def new_random(m, n_datums=0):
        ds = DataSet(
            market = m,
            is_training = True)
        ds.save()

        for i in range(n_datums):
            dat = ds.add_datum()
            # don't forget to increase the count of data points
            ds.datum_count += 1
        ds.save()

    # creates a new dataset from a file
    # TODO: implement it; add schema as param?
    def new_from_file(market, file):
        pass

    def __str__(self):
        return "dataset #%d" % (self.id)

class Datum(models.Model):
    # the set this data point is part of
    data_set = models.ForeignKey(DataSet)
    # the test data
    x = models.CharField(max_length=1024)
    # the actual outcome for the event x
    y = models.ForeignKey(Outcome)
    # the consecutive id of the datum in the set
    set_id = models.IntegerField()

    def __str__(self):
        return "datum #%d from %s" % (self.set_id, self.data_set)

class Order(models.Model):
    # the account that made the order
    account = models.ForeignKey(Account)
    # for which dataset entry (datum) was the bet made
    datum = models.ForeignKey(Datum)
    # when is the order made
    timestamp = models.DateTimeField('Time created')
    # whether the order is processed
    is_processed = models.BooleanField(default=False)
    # whether the order is cancelled
    def get_position(self, outcome):
        try:
            return self.position_set.get(outcome=outcome).amount
        except ObjectDoesNotExist:
            return 0
        except MultipleObjectsReturned:
            raise Exception("Too many positions for order %d! Invalid state?.. " % (self.id))
        
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
        for (out, amount) in position:
            pos = Position.new(order, out, amount)
            pos.save()
        return order


    def cancel(self):
        self.delete()
    
# represents a position on a given outcome
# in the context of an order. 
class Position(models.Model):
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

# contains uploaded documents, as defined in settings.py
class Document(models.Model):
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