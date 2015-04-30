ml-market
=========

**ml-market** is a software for creating online machine learning or prediction markets written in Python using the Django web framework. In comparison to existing solutions it provides a flexible market maker architecture and a RESTful API for market interaction. 

Machine learning markets are a type of prediction markets where a number of traders interact with a central market authority (a _market maker_) with the purpose of making predictions concerning the possible outcomes of some unknown event. Markets should be made in such a way as to incentivise participants to bet according to their true beliefs in order to obtain a reliable estimate on the outcome of the event. 

# Installation

You will need Python 3.3+ and the following components from your favourite package manager for Python (e.g. `pip`):

| Component Name       | Package Name       |
|----------------------|-------------------:|
|Django                |django              |
|Django REST Framework |djangorestframework |
|Django Extensions     |django-extensions   |
|Django Enum Fields    |django-enumfields   |


Once you have those, grab the latest source code from [Github](https://github.com/ixtreon/ml-market). 

Once inside the root directory of the project you can create the required database models by running:
	
	python manage.py makemigrations

followed by:

	python manage.py migrate

This should create the underlying SQLite database tables using the default provider. 
If you want to change the database back-end to something more suitable for use in production please refer to the [Django documentation](https://docs.djangoproject.com/en/1.7/ref/databases/) on this topic. 


To then start the Django test server run:

    python manage.py runserver

from inside the main project directory. 


You can then browse to http://127.0.0.1:8000/admin/ to create or manage markets or to http://127.0.0.1:8000/ to visit the main site. 

# Tests

To run the existing unit tests navigate to the root directory of the project and run:

	python manage.py test market.tests

# Documentation

Visit http://ixtreon.github.io/ml-market/

# Structure

The **markets** module defines the markets' core structure and its web views; it also includes a simple admin interface for their management. 

In a _market_ participants place _orders_ (subject to the funds in their _account_) with their predictions on the possible _outcomes_ of a set of _events_. In other words they choose the amount of contracts associated with an outcome to purchase, where each contract promises a payment of a credit if its associated _outcome_ happens to be the actual _result_ of the _event_. 

Note that this module does not handle in any way the orders it receives but simply raises the `order_received` signal to announce their arrival. It is up to another module to hook to the signal and e.g. modify the user's funds or the published prices. (actually it creates its own market maker and hooks it)



# Market Makers

The **msr-maker** module is an implementation of the logarithmic market scoring rule (Hanson et al.) market maker. It listens for orders and instantly matches them calculating a price based on the current holdings of the market maker and the liquidity constant. 

The **order_book** module contains a bare-bones order book maker which is considerably simpler than the msr-maker. 

# TODO
+ Support for structured input (xml or json)
