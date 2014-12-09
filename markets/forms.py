from django import forms
from markets.models import Market, Outcome, Order, Document, Event
from django.core import validators
from _decimal import Decimal
from django.forms import widgets
import json
from django.core.serializers.json import DjangoJSONEncoder
 
class MarketForm(forms.Form):
    # the market this form is about
    market = None
    # all outcomes connected to that market
    events = None
    # the account the user is logged in with
    account = None
    # the (single bet) claim the user has selected 
    claim = None
    # the (single bet) amount the user has selected
    amount = forms.DecimalField(
        initial=0,
        max_digits=6, 
        decimal_places=2,
        widget = widgets.NumberInput(attrs = { 'onchange': 'validate_amount(this)'}))
    
    # the (multi bet) position the user has chosen
    position = []

    template_name = 'market/detail.html'

    errors = {}

    def validate(self):
        self.errors = {}

        # TODO: restore server-side validation
        # Note this doesn't check for forged orders
        # the market maker should perform validation anyway. 

        #    # check if amount is non-null, valid and not greater than current funds
        #    if self.amount == None:
        #        self.errors['amount'] = "Please select the amount to bet. "
        #    elif self.amount > self.account.funds:
        #        self.errors["amount"] = "You've bet more than you have!"
        #    elif self.amount < 0:
        #        pass    # for now

        return len(self.errors) == 0 



    def json_prices(self):
        "Gets the outcomes' current prices in json format. "
        z = dict(Outcome.objects.filter(event__market=self.market).values_list('id', 'current_price'))
        return json.dumps(z, cls=DjangoJSONEncoder)

    # Gets the user order information
    # from the POST request
    def read_post_position(self, post):
        pos = []
        for ord in self.outcomes:
            try:
                ord_pos = int(post["pos_%i" % (ord.id)])
            except:
                ord_pos = 0

            if ord_pos != 0:
                pos.append((ord, ord_pos))
        return pos

    def __init__(self, market, account, *args, **kwargs):
        self.market = market
        self.market_active = market.is_active()
        self.events = [ (e.description, e.outcomes.all()) for e in market.events.all()]
        self.outcomes = list(Outcome.objects.filter(event__market=self.market))

        self.account = account

        # get the outcome prices in json to pass to the template
        self.prices = self.json_prices()

        if account:
            # get all the standing orders of the user
            self.orders = [ord.get_data(self.outcomes) for ord in account.standing_orders()]

            if kwargs.get('post'):
                post = kwargs['post']
                self.position = self.read_post_position(post)

        super(MarketForm, self).__init__()


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