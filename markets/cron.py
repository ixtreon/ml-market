
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone
from threading import Thread
import time

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## TODO: hook reveal_interval or challenge_start getting changed
class Cron():

    cron = scheduler(lambda: timezone.now().timestamp())

    def start(self):
        "Starts the cron scheduler on a new thread. "
        # get all active datasets
        active_sets = set(DataSet.objects.filter(is_active=True))
        print("Loaded %d active sets" % len(active_sets))
        # and start tracking them
        for s in active_sets:
            self.advance_set(s)

        self.thread = Thread(target=self.cron.run, daemon=True)
        self.thread.start()

    def advance_set(self, set):
        """Advances the dataset to its current datum and re-tracks it if it is still active afterwards. 
Executed whenever a set expires. """

        t = timezone.now()
        while set.challenge_end() <= t:
            if not set.next():
                break
            print("Advanced data-set %s" % set)

        if set.is_active:
            end = set.challenge_end()
            assert end > t
            print("Tracking data-set %s" % str(set))
            self.cron.enterabs(end.timestamp(), 1, Cron.advance_set, kwargs={'set': set})