ml-market
=========

**ml-market** is a software for creating online machine learning markets and is written in Python with the help of Django and jQuery. 

Machine learning markets are a type of prediction markets where a number of traders interact with a central market authority (a _market maker_) with the purpose of making predictions concerning the possible outcomes of some unknown event. Markets should be made in such a way as to incentivise participants to bet according to their true beliefs in order to obtain a reliable estimate on the outcome of the event. 

# Installation
You will need Python 3.3 and Django 1.7. Once you have them grab the latest source code from [Github](https://github.com/ixtreon/ml-market). Then run:

    python manage.py runserver
from inside the main directory to start the test web-server. 

You can then browse to http://127.0.0.1:8000/admin/ and create new markets. 

# Structure

The **markets** module defines the markets' core structure and its web views; it also includes a simple admin interface for their management. 

In a _market_ participants place _orders_ (subject to the funds in their _account_) with their predictions on the possible _outcomes_ of a set of _events_. In other words they choose the amount of contracts associated with an outcome to purchase, where each contract promises a payment of a credit if its associated _outcome_ happens to be the actual _result_ of the _event_. 

Note that this module does not handle in any way the orders it receives but simply raises the `order_received` signal to announce their arrival. It is up to another module to hook to the signal and e.g. modify the user's funds or the published prices. (actually it creates its own market maker and hooks it)


The **msr-maker** module is a bare-bones implementation of the logarithmic market scoring rule (Hanson et al.) market maker. It listens for orders and instantly matches them calculating a price based on the current holdings of the market maker and the liquidity constant. 

# TODO
+ Support for structured input (xml or json)
+ Installation should mention database setup, user accounts, admin pages usage. 
