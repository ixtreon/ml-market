from django.core.management.base import BaseCommand, CommandError
from markets.models import Order
from time import sleep

def periodic(f, t = 1):
    while True:
        f()
        sleep(t)

### UNUSED!! ###
class Command(BaseCommand):
    help = 'Runs the market. '
        

    def handle(self, *args, **options):
        periodic(Command.check_orders)
        
    def check_orders():
        ords = Order.unprocessed_orders()
        if ords.count() > 0:
            print(str(len(ords)))