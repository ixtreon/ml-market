from django.db import models
from markets.models import Outcome, DecimalField
from django.core.exceptions import MultipleObjectsReturned


class Supply(models.Model):
    outcome = models.ForeignKey(Outcome, on_delete=models.DO_NOTHING)
    amount = DecimalField()

    def get(outcome):
        try:
            sup = Supply.objects.get(outcome=outcome)
        except models.ObjectDoesNotExist:
            sup = Supply(outcome=outcome)
            sup.save()
        except MultipleObjectsReturned:
            raise Exception("Too many supplies for a single outcome! Invalid state?.. ")
        return sup

    def for_event(ev):
        return { out: Supply.get(out).amount for out in ev.outcomes.all() }
