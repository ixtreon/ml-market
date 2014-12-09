
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone
from threading import Thread
import time
from markets.signals import dataset_change
from functools import partial

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
## TODO: hook reveal_interval or challenge_start getting changed
class Cron():
    
    # contains a tuple of job_id, job_end_time
    jobs = dict()
    cron = scheduler(lambda: timezone.now().timestamp())

    def set_changed(self, **kwargs):
        set = kwargs['set']
        print("Set changed: %s" % set)
        set_tracked = set in self.jobs


    def start(self):
        "Starts the cron scheduler on a new thread. "
        dataset_change.connect(partial(Cron.set_changed, self))
        # get all active datasets
        active_sets = set(DataSet.objects.filter(is_active=True))
        print("Loaded %d active sets" % len(active_sets))
        # and start tracking them
        for s in active_sets:
            self.advance_set(s)

        self.thread = Thread(target=self.cron.run, daemon=True)
        self.thread.start()

    def advance_set(self, set):
        """Advances this dataset to its current challenge and adds it to the scheduler, if necessary. """
        # leaves them sync'd
        t_now = timezone.now()

        # advance to the current challenge
        while set.is_active and set.challenge_end() <= t_now:
            if not set.next():
                break
            print("Advanced data-set %s" % set)

        if set.is_active:   # if there's a current challenge
            # add the set's expiration date to the scheduler
            assert (set not in self.jobs)
            t_end = set.challenge_end()
            assert t_end > t_now
            job_id = self.cron.enterabs(t_end.timestamp(), 1, Cron.advance_set, kwargs={'set': set})
            self.jobs[set] = (job_id, t_end)
            print("Tracking data-set %s" % str(set))
        else:
            # explicitly untrack the set??
            # might come here if cron/jobs are not sync'd
            (job_id, t_end) = self.jobs.pop(set, (None, None))
            if job_id:
                self.cron.cancel(job_id)
