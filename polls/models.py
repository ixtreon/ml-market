import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Claim(models.Model):
    description = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')
    real_outcome = models.OneToOneField('Outcome', related_name='ans', null=True, blank=True)

    def __str__(self):
        return self.description

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Outcome(models.Model):
    claim = models.ForeignKey(Claim)
    name = models.CharField(max_length=255)
    price = models.IntegerField(default=0)

    def __str__(self):
        return str(self.claim) + " " + self.name


class Coupon(models.Model):
    outcome = models.ForeignKey(Claim)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.bet) + ' for ' + str(self.choice)