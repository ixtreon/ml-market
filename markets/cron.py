
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone
from threading import Thread

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## UNUSED !!
## TODO: move file?
class Cron():

    cron = scheduler(timezone.now)

    

    def start(self):
        "Starts the cron scheduler on a new thread. "
        # get all active datasets
        active_sets = set(DataSet.objects.filter(is_active=True))
        print("Loaded %d active sets" % len(active_sets))
        # and start tracking them
        for s in active_sets:
            Cron.advance_set(s)

        self.thread = Thread(target=self.cron.run, daemon=True)
        self.thread.start()

    def track(self, set):
        "Start tracking this dataset for expiration. "
        print("Start tracking %s" % set)
        self.cron.enterabs(set.challenge_end(), 1, Cron.advance_set, kwargs={'set': set})

    def advance_set(set):
        """Advances the dataset to its current datum and re-tracks it if it is still active afterwards. 
Executed whenever a set expires. """

        t = timezone.now()
        while set.challenge_end() <= t:
            if not set.next():
                break
            print("Advanced data-set %s" % set)

        if set.is_active:
            assert set.challenge_end() > t
            print("Tracking data-set %s" % set)
            Cron.track(s)