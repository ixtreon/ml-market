from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from markets.models import Market, Account, Document, Order, Outcome
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import generic
from django import forms
from markets.forms import MarketForm, UploadForm, UserForm

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
# TODO: user accounts
@login_required
def user_info(request):
    form = UserForm(request.user)
    return render(request, 'user.html', {
        'form': form,
        })

# displays a market along with an order form for the user. 
@login_required
def market_view(request, pk):
    
    market_id = int(pk)
    m = get_object_or_404(Market, id=market_id)
    try:
        a = request.user.account_set.get(market=m)
    except Account.DoesNotExist:
        a = None

    if request.method == 'POST' and a != None:
        # A POST request: Handle Form Upload
        form = MarketForm(m, a, post=request.POST) # Bind data from request.POST into a form
        
        ord = a.place_multi_order(m, form.position)
        
        form.orders.append(ord.get_data(m.outcome_set.all()))
    else:
        form = MarketForm(m, a)

 
    return render(request, 'market/index.html', {
        'form': form,
        })

# Handles a user willing to join a specific market. 
@login_required
def market_join(request, qid):
    m = get_object_or_404(Market, id=qid)
    u = request.user

    if m.get_user_account(u) == None:
        a = Account(user=u, market=m, funds=100)
        a.save()

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
        print("upload request received.. ")
        try:
            file_data = request.FILES['file']
        except:
            return HttpResponseRedirect(reverse('upload'))
        newdoc = Document(
            file = file_data,
            user = u)
        newdoc.save()
        print("upload request accepted: '%s'" % file_data)
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