import django.dispatch

# raised when a user places an order
order_placed = django.dispatch.Signal(providing_args=["order"])

# raised whenever a dataset is changed
dataset_change = django.dispatch.Signal(["set"])