
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone
from threading import Thread
import time
from markets.signals import dataset_change
from functools import partial

from markets.log import logger

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## TODO: hook reveal_interval or challenge_start getting changed
class Cron():
    
    jobs = dict()       # contains (cron_id, end_time) for each job
    cron = scheduler(lambda: timezone.now().timestamp())

    # executed when any of the datasets change. 
    def dataset_changed(self, **kwargs):
        set = kwargs['set']
        print("Set changed: %s" % set)
        is_tracked = set in self.jobs


    def start(self):
        "Starts the cron scheduler on a new, separate thread. "
        # connect to the set changed event
        dataset_change.connect(partial(Cron.dataset_changed, self))
        # get all the active sets
        active_sets = set(DataSet.objects.filter(is_active=True))
        logger.info("Found %d currently active sets. " % len(active_sets))

        # advance (if necessary) and start tracking them
        for s in active_sets:
            self.advance_set(s)

        self.thread = Thread(target=self.cron.run, daemon=True)
        self.thread.start()

    def advance_set(self, set):
        """Advances this dataset to its current challenge and adds it to the scheduler, if necessary. """
        t_now = timezone.now()

        # advance to the current challenge
        while set.is_active and set.challenge_end() <= t_now:
            if not set.next():
                break

        if set.is_active:   # if there's a current challenge
            # re-add the set to the scheduler
            assert (set not in self.jobs)
            t_end = set.challenge_end()
            assert t_end > t_now
            job_id = self.cron.enterabs(t_end.timestamp(), 1, Cron.advance_set, kwargs={'set': set})
            self.jobs[set] = (job_id, t_end)
            logger.info("Tracking challenge #%d of data-set %s" % (set.active_datum_id, str(set)))

