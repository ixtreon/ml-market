from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from polls.models import Market, Account, Document, Order, Outcome
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views import generic
from django import forms
from polls.forms import MarketForm, UploadForm, UserForm

@login_required
def index(request):

    markets = Market.objects.order_by('-pub_date')[:15]
    return render(request, 'market/index.html', {
        'markets': markets,
        })

class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'markets'
    
    # returns all markets (no paging whatsoever)
    def get_queryset(self):
        return Market.objects.order_by('-pub_date')



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
        form = MarketForm(m, a, post=request.POST) # Bind data from request.POST into a PostForm
        outcome = Outcome.objects.get(id=form.claim)

        # If data is valid, proceeds to create a new post and redirect the user
        if form.validate():
            print("valid form\nCreating order")
            a.place_order(m, outcome, form.amount)
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

    return HttpResponseRedirect(reverse('polls:market', args=(m.id,)))

# handles users uploading files
# TODO: file verification, size check, management
@login_required
def upload_file(request, **kwargs):

    u = request.user

    # Handle file upload
    if request.method == 'POST':
        form = UploadForm(u, request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(
                file = request.FILES['file'],
                user = u)
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('upload'))
    else:
        form = UploadForm(u) # A empty, unbound form

    # Load documents for the list page
    try:
        documents = Document.objects.filter(user=u)
    except:
        documents = None

    print(documents)
    # Render list page with the documents and the form
    return render(request, 'upload.html', {
        'form': form,
        'documents': documents,
    })