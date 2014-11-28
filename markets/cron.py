
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## UNUSED !!
## TODO: move file?
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
            if not s.next():
                active_sets.remove(s)
            s.save()

        # track all data sets
        for s in active_sets:
            Cron.track(s)

    def run(new_thread=True):
        "Starts the update scheduler. "
        pass

    def next_challenge(set):
        if not s.next():
            active_sets.remove(s)
        s.save()

    def track(self, set):
        "Start tracking this dataset's expiration. "
        end = set.challenge_end()
        print("Start tracking %s" % set)
        self.cron.enterabs(end, 1, set_expire, kwargs={'set': set})

    def set_expire(set):
        """Advances the dataset until it's over or its expiration is in the future. 
Run whenever a set expires. """

        t = timezone.now()
        while set.challenge_end() <= t and set.next():
            pass
            print("Advanced data-set %s" % set)

        if set.is_active:
            assert set.challenge_end() > t
            print("Tracking data-set %s" % set)
            Cron.track(s)