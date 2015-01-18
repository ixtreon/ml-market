from django.db import models
from markets.models import Outcome, DecimalField
from django.core.exceptions import MultipleObjectsReturned


class MsrSupply(models.Model):
    outcome = models.OneToOneField(Outcome)
    amount = DecimalField()

    def get(outcome):
        try:
            sup = outcome.msrsupply
        except models.ObjectDoesNotExist:
            sup = MsrSupply(outcome=outcome)
            sup.save()
        except MultipleObjectsReturned:
            raise Exception("Too many supplies for a single outcome! Invalid state?.. ")
        return sup

    def for_event(ev):
        return { out: MsrSupply.get(out).amount for out in ev.outcomes.all() }
