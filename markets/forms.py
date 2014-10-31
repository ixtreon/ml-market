from django import forms
from markets.models import Market, Outcome, Order, Document
from django.core import validators
from _decimal import Decimal
from django.forms import widgets
 
class MarketForm(forms.Form):
    # the market this form is about
    market = None
    # all outcomes connected to that market
    outcomes = None
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

    #    # check if claim is non-null and a valid one. 
    #    if self.claim == None:
    #        self.errors['claim'] = "Please select a claim. "
    #    elif self.market.outcome_set.filter(id=self.claim).count() != 1:
    #        self.errors['claim'] = 'Please select a valid claim. '

    #    # check if amount is non-null, valid and not greater than current funds
    #    if self.amount == None:
    #        self.errors['amount'] = "Please select the amount to bet. "
    #    elif self.amount > self.account.funds:
    #        self.errors["amount"] = "You've bet more than you have!"
    #    elif self.amount < 0:
    #        pass    # for now

        return len(self.errors) == 0 

    

    def __init__(self, market, account, *args, **kwargs):
        self.market = market
        self.outcomes = market.outcome_set.all()
        self.account = account
        # all orders the user has made so far
        self.orders = [ord.get_data(self.outcomes) for ord in account.standing_orders()]
        # the current prices
        self.price_list = "[%s];" % (", ".join([str(o.current_price) for o in self.outcomes]))
        print(self.orders)
        if kwargs.get('post'):
            post = kwargs['post']
            # get the user position
            self.position = []
            for o in self.outcomes:
                k = "pos_%i" % (o.id)
                try:
                    v = int(post[k])
                except:
                    v = 0

                print("user wants %d contracts for outcome %s" % (v, o))
                self.position.append((o, v))

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