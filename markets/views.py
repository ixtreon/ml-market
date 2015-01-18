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

@login_required
def index(request):

    markets = Market.objects.order_by('-pub_date')[:15]

    return render(request, 'market/index.html', {
        'markets': markets,
        })

class IndexView(generic.ListView):
    template_name = 'all-markets.html'
    context_object_name = 'markets'
    
    # returns all markets (no paging whatsoever)
    def get_queryset(self):
        return [m for m in Market.objects.order_by('-pub_date') if m.is_active()]



# displays user information
@login_required
def user_info(request):
    form = UserForm(request.user)
    return render(request, 'user.html', {
        'form': form,
        })

# displays market bet form
@login_required
def market_bet(request, pk):
    pass


# displays orders the user has made
@login_required
def market_view_orders(request, pk):
    pass


# displays a market along with an order form for the user. 
@login_required
def market_index(request, pk):
    
    market_id = int(pk)
    m = get_object_or_404(Market, id=market_id)
    a = m.primary_account(request.user)

    if request.method == 'POST' and a != None:
        # user wants to post a message
        form = MarketForm(m, a, post=request.POST) # Bind data from request.POST into a form
        # place the order
        ord = a.place_order(m, form.position)
        # adds the newly created order to the form before displaying it. 
        form.orders.append(ord.get_data(form.outcomes))
    else:   # just display the market page
        form = MarketForm(m, a)

 
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
    ord.cancel()
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