from django import forms
from markets.models import Market, Outcome, Order, Document, Event, AccountBalance
from django.core import validators
from _decimal import Decimal
from django.forms import widgets
import json
from django.core.serializers.json import DjangoJSONEncoder
 
class OutcomeData():
    """
    Contains the common information for an outcome and a given account. 
    """
    def __init__(self, acc, out):
        self.outcome = out
        self.account = acc
        if acc:
            self.amount = AccountBalance.get(acc, out).amount

class MarketForm(forms.Form):
    # the market this form is about
    market = None
    # all outcomes connected to that market
    events = None
    # the account the user is logged in with
    account = None
    # the (single bet) claim the user has selected 
    claim = None
    
    # the (multi bet) position the user has chosen
    position = []

    template_name = 'market/detail.html'


    def json_prices(self):
        "Dumps the current prices of this market's outcomes in json format. "
        outcomes = Outcome.objects.filter(event__market=self.market)
        outcome_list = outcomes.values_list('id', 'current_price')
        outcome_dict = dict(outcome_list)

        return json.dumps(outcome_dict, cls=DjangoJSONEncoder)


    def __init__(self, market, account, *args, **kwargs):
        self.market = market
        self.market_active = market.is_active()
        self.events = [ (e, [OutcomeData(account, out) for out in e.outcomes.all()]) for e in market.events.all()]
        self.outcomes = list(Outcome.objects.filter(event__market=self.market))

        self.account = account

        # get the outcome prices in json to pass to the template
        self.prices = self.json_prices()


        if account:
            # get all orders from this user
            self.orders = [ord.get_data(self.outcomes) for ord in account.all_orders()]

            if kwargs.get('post'):
                post = kwargs['post']
                self.position = market.parse_bid(post)


        super(MarketForm, self).__init__()

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ()
    

    def __init__(self, acc, *args, **kwargs):

        super().__init__(self, *args, **kwargs)
        self.account = acc
        self.outcomes = [OutcomeData(acc, out) for out in self.instance.outcomes.all()]

class UploadForm(forms.Form):
    # file to be currently uploaded. 
    file = forms.FileField(
        label = "Select a file",
        help_text='max. ?? megabytes. ')

    # already uploaded files
    file_list = forms.ModelMultipleChoiceField(
        queryset=None,)

    def __init__(self, u, *args, **kwargs):
        super(UploadForm, self).__init__()
        user_docs = Document.objects.filter(user=u)
        self.docs_present = user_docs.count()
        self.fields['file_list'].queryset = user_docs


class UserForm(forms.Form):
    user = None

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserForm, self).__init__(*args, **kwargs)