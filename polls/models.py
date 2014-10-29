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

# Create your models here.
def DecimalField():
    return models.DecimalField(default=0, decimal_places=2, max_digits=7)

def t():
    return timezone.now()

class Market(models.Model):
    description = models.CharField(max_length=255, default='Add a description here. ')
    pub_date = models.DateTimeField('Date Started')
    exp_date = models.DateTimeField('Expiration Date', default=t)
    # interval between challenge revelations
    reveal_interval = models.IntegerField('Interval between challenges', default=1)
    # date last challenge was revealed
    last_revealed_id = models.IntegerField('Current challenge id', default = -1)
    last_reveal_date = models.DateTimeField('Date Last Challenge started', default=t)

    def get_current_datum(self):

        pass

    def get_user_account(self, u):
        try:
            return u.account_set.get(market=self)
        except Account.DoesNotExist:
            return None

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
    
    @transaction.atomic
    def place_order(self, market, outcome, amount):
        try:
            order = Order.new(market, self, outcome, amount)
        except Exception as err:
            raise Exception("failed creating an order: " + str(err))
        
        print("wohoo, made an order! Now saving. ")
        self.funds -= amount

        self.save()
        order.save()

# represents an outcome in a multiclass market. 
class Outcome(models.Model):
    market = models.ForeignKey(Market)

    name = models.CharField(max_length=255)
    current_price = DecimalField()

    def __str__(self):
        return self.name + " : " + str(self.current_price)

# 
class DataSet(models.Model):
    market = models.ForeignKey(Market)
    is_training = models.BooleanField(default=False)
    datum_count = models.IntegerField(default=0)
    


    def addDatum(self, x = "", y = None):
        if y == None:
            outcomes = list(self.market.outcome_set.all())
            n_outcomes = len(outcomes)
            random_outcome_id = random.randint(0, n_outcomes-1)   # range is inclusive at both ends
            y = outcomes[random_outcome_id]
            print("Generated datum #%d with a random outcome: '%s'" % (self.datum_count, y))

        if x == "":
            x = self.market.description + " " + str(self.datum_count)

        dat = Datum()
        dat.x = x
        dat.y = y
        dat.setId = self.datum_count
        dat.data_set = self
        dat.save()

    def newTrain(m, n_datums=0):
        outcomes = list(m.outcome_set.all())
        n_outcomes = len(outcomes)

        ds = DataSet()
        ds.market = m
        ds.is_training = True
        ds.save()

        for i in range(n_datums):
            dat = ds.addDatum()
            # don't forget to increase the count of data points
            ds.datum_count += 1
        ds.save()

    def __str__(self):
        return "dataset #%d" % (self.id)

class Datum(models.Model):
    # the test data
    # TODO: fix its type..
    x = models.CharField(max_length=1024)

    # the actual outcome for the event x
    y = models.ForeignKey(Outcome)

    # the consecutive id of the datum in the set
    setId = models.IntegerField()

    # the set this data point is part of
    data_set = models.ForeignKey(DataSet)

    def __str__(self):
        return "datum #%d from %s" % (self.setId, self.data_set)

class Order(models.Model):
    # for which datum (iteration) was the bet made
    datum = models.ForeignKey(Datum)

    # what do we bet on
    claim = models.ForeignKey(Outcome)

    # at what price do we want to buy/sell
    price = DecimalField()

    # how much we put in
    amount = DecimalField()

    # when is the order made
    timestamp = models.DateTimeField('Time created')

    # creates a new order for the given account playing on the given market. 
    # looks up the current challenge for that market
    # looks up its current price
    def new(market, account, outcome, _amount):

        # get the current challenge datum id
        datumId = market.last_revealed_id
        if(datumId < 0):
            raise Exception("No current challenge for this market!")


        # get the current training set
        dataSets = market.dataset_set.filter(is_training=True)
        nTrain = dataSets.count()
        if nTrain == 0:
            raise Exception("No training sets in this market!")
        if nTrain > 1:
            print("Warning: more than 1 training sets. Are they well handled? (no)")
        
        # get the datum with this id
        dataSet = dataSets.first()
        try:
            d = dataSet.datum_set.get(setId=datumId)
        except ObjectDoesNotExist:
            raise Exception("No challenge with with such setId!")
        except MultipleObjectsReturned:
            raise Exception("Too many challenges with this id! Corrupted db?.. ")

        return Order(
            datum = d,
            claim = outcome,
            amount = _amount,
            timestamp = timezone.now())
    
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
        return self.fileName() + str(self.exists())