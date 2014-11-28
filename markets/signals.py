import django.dispatch

order_placed = django.dispatch.Signal(providing_args=["order"])

datum_changed = django.dispatch.Signal(providing_args=["set"])
