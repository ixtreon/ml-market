from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from markets.models import Market, Account, Document, Order, Outcome
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import generic
from django import forms
from markets.forms import MarketForm, UploadForm, UserForm

from markets.log import logger
from django.http.response import HttpResponse
import json
from django.contrib.auth.models import User

@login_required
def index(request):

    markets = Market.objects.order_by('-pub_date')[:15]

    return render(request, 'market/index.html', {
        'markets': markets,
        })

class MarketIndexView(generic.ListView):
    template_name = 'all-markets.html'
    context_object_name = 'markets'
    
    # returns all markets (no paging whatsoever)
    def get_queryset(self):
        markets = [m for m in Market.objects.order_by('-pub_date') if m.is_active()]
        return markets

    def get_context_data(self, **kwargs):
        # Call the base first to get a context
        context = super().get_context_data(**kwargs)
        # Then append to each market the current user's funds
        u = self.request.user
        for m in context['markets']:
            usr_mkt_account = m.primary_account(u)
            if usr_mkt_account:
                m.primary_funds = usr_mkt_account.funds
        return context


# displays user information
@login_required
def user_info(request, uid):
    if uid:
        user = get_object_or_404(User, username=uid)
    else:
        user = request.user
    form = UserForm(user)
    return render(request, 'user/index.html', {
        'form': form,
        })


def market_activity(request, pk):
    response_data = {}
    m = get_object_or_404(Market, id=int(pk))


    response_data['bur'] = 'kek'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


# displays a market along with an order form for the user. 
@login_required
def market_index(request, pk):
    
    market_id = int(pk)
    mkt = get_object_or_404(Market, id=market_id)
    acc = mkt.primary_account(request.user)

    if request.method == 'POST' and acc != None:
        # user wants to post a bid
        form = MarketForm(mkt, acc, post=request.POST) # Bind data from request.POST into a form

        # parse the position from the POST data
        self.position = mkt.parse_bid(post)

        # place the order
        ord = acc.place_order(mkt, form.position)
        
        # adds the newly created order to the form before displaying it. 
        # ONLY if the order was successfully created (i.e. non-empty)
        if ord:
            form.orders.append(ord.get_data(form.outcomes))
    else:   # just display the market page
        form = MarketForm(mkt, acc)

 
    return render(request, 'market/index.html', {
        'form': form,
        })

# Handles a user willing to join a specific market. 
@login_required
def market_join(request, pk):
    m = get_object_or_404(Market, id=pk)
    u = request.user

    if not m.primary_account(u):
        m.create_primary_account(u)
    return HttpResponseRedirect(reverse('markets:market', args=(m.id,)))

# Handles a user willing to discard a standing (!) order
@login_required
def order_remove(request, pk):
    u = request.user
    ord = get_object_or_404(Order, account__user=u, id=pk)
    m = ord.account.market
    ord.cancel()     # throws an exception for invalid orders
    return HttpResponseRedirect(reverse('markets:market', args=(m.id,)))

# handles users uploading files
# TODO: file verification, size check, management
@login_required
def upload_file(request, **kwargs):

    u = request.user

    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(u, request.POST, request.FILES)

        try:
            file_data = request.FILES['file']
        except:
            return HttpResponseRedirect(reverse('upload'))
        newdoc = Document(
            file = file_data,
            user = u)
        newdoc.save()
        logger.info("User %s uploaded file '%s'" % (str(u), file_data))
        # Redirect to the document list after POST
        return HttpResponseRedirect(reverse('upload'))
    else:
        form = UploadForm(u) # A empty, unbound form

    ## Load documents for the list page
    #try:
    #    documents = Document.objects.filter(user=u)
    #except:
    #    documents = None

    # Render list page with the form
    return render(request, 'upload.html', {
        'form': form,
    })