
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## UNUSED !!
class Cron():

    cron = scheduler(timezone.now)

    def __init__(self):
        t = timezone.now()
        # get all active datasets
        active_sets = set(DataSet.objects.filter(is_active=True))
        
        print("Loaded %d active sets" % len(active_sets))

        # get the expired datasets
        expired_sets = set(s for s in active_sets if s.challenge_end() < t)
        print("%d sets have expired since the last start. " % (len(expired_sets)))
        for s in expired_sets:
            try:
                s.next_challenge()
            except:
                s.is_active = False
                active_sets.remove(s)
            s.save()

        # track all data sets
        for s in active_sets:
            Cron.track(s)

    def run(new_thread=True):
        "Starts the update scheduler. "
        pass

    def track(self, set):
        "Start tracking this dataset's expiration. "
        end = set.challenge_end()
        self.cron.enterabs(end, 1, set_expire, kwargs={'set': set})

    def set_expire(set):
        "Executed whenever a set expires. "
        pass