
from markets.models import DataSet
from sched import scheduler
from django.utils import timezone
from threading import Thread, Timer
import time
from markets.signals import dataset_change
from functools import partial

from markets.log import logger

## Schedules updates to the markets' active challenges. 
## Runs on a thread different than the main one. 
class Cron():
    """Schedules challenge expirations. """
    
    # static
    instance = None     # The cron instance that is currently running. 

    jobs = dict()       # keeps (set, end_time, cron_id) for each market job. 

    cron = scheduler(lambda: timezone.now().timestamp())

    @staticmethod
    def dataset_changed(**kwargs):
        """Executed in response to the dataset_changed signal.
Makes sure the cron tracker is up-to-date. """
        self = Cron.instance
        set = kwargs['set']
        mkt = set.market

        # see whether we should track this set/market
        if set.is_active:
            track_new = set.challenge_end()
        else:
            track_new = None

        # see how we track the market/set now
        if mkt in self.jobs:
            track_cur = self.jobs[mkt][1]
        else:
            track_cur = None

        # print("%s <-> %s" % (track_cur, track_new))

        # proceed only if stuff changed
        if track_cur == track_new:
            return

        if track_cur:
            print("Untracking %s. Ends at %s" % (self.jobs[mkt][:2]))
            self.jobs[mkt][2].cancel()
            del self.jobs[mkt]

        if track_new:
            self.add(mkt, set, track_new)





    def start(self):
        "Starts the cron scheduler on a new, separate thread. "

        # allow only one instance running
        if Cron.instance != None:
            raise Exception("Cron is already running!")
        Cron.instance = self

        # connect to the set changed event
        dataset_change.connect(Cron.dataset_changed)

        # start the cron
        self.thread = Thread(target=self.cron.run, daemon=True)
        self.thread.start()

        # get all the active datasets
        active_sets = set(DataSet.objects.filter(is_active=True))
        if not active_sets:
            logger.info("[Cron] No active markets. ")
            return

        logger.info("Tracking %d currently active market(s): %s" 
                    % (len(active_sets), ", ".join([str(s.market) for s in active_sets])))

        # advance and start tracking the active sets, if needed
        for s in active_sets:
            self.advance_set(s)

    @staticmethod
    def advance_set(set):
        """Advances this dataset to its current challenge and adds it to the scheduler, if necessary. """

        self = Cron.instance
        t_now = timezone.now()
        mkt = set.market
        
        if not set.is_active:
            return

        # make sure we haven't tracked this market already
        if mkt in self.jobs:
            if self.jobs[mkt][0] != set:
                logger.warn("[Cron] Changed dataset for market '%s' from '%s' to '%s'" % (mkt, self.jobs[mkt][0], set))
            del self.jobs[mkt]

        # advance to the next challenge
        while set.is_active and set.challenge_expired():
            set.next()

        if set.is_active:   # if there's a current challenge
            assert (not set.challenge_expired())    # current chalenge must have expired

            
            # re-add the set to the scheduler
            t_end = set.challenge_end()
            self.add(mkt, set, t_end)

    def add(self, mkt, set, t_end):
        """Executes the advance_set() method in t_end seconds with ``set`` as the argument. """
        

        t_left = t_end - timezone.now()

        if t_left.total_seconds() < 0:
            return

        t = Timer(t_left.total_seconds(), Cron.advance_set, kwargs={'set': set})
        t.daemon = True
        t.start()
        self.jobs[mkt] = (set, t_end, t)
        #print("Tracking %s. Ends at %s" % (self.jobs[mkt][:2]))
