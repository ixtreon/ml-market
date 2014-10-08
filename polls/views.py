from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from polls.models import Claim

def index(request):
    claims = Claim.objects.order_by('-pub_date')[:15]
    context = {'claims': claims}
    return render(request, 'market/index.html', context)

def claim(request, qid):
    qid = int(qid)
    c = get_object_or_404(Claim, id=qid)

    return render(request, 'market/detail.html', {'claim': c})

def bid(request, qid):
    claim = get_object_or_404(Claim, id=qid)
    try:
        o = claim.outcome_set.get(id=request.POST['choice'])
    except (KeyError, Claim.DoesNotExist):
        return render(request, 'market/detail.html', {
            'claim': claim,
            'error_message': "You didn't select a choice.",
        })
    else:
        o.price += 1
        o.save()

        return HttpResponseRedirect(reverse('polls:market', args=(claim.id,)))