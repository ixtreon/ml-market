from django.core.management.base import BaseCommand, CommandError
from markets.models import Order
from time import sleep

def periodic(f, t = 1):
    while True:
        f()
        sleep(t)

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)
        


    def handle(self, *args, **options):
        periodic(Command.zurla)
        
    def zurla():
        ords = Order.unprocessed_orders()
        if ords.count() > 0:
            print("qj kur: " + str(len(ords)))