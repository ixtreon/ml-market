
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from markets.models import Order, Market


@api_view(['POST', 'GET'])
@permission_classes((IsAuthenticated, ))
def api_bid(request, mkt):
    """
    Creates a new order for the specified market. 
    """

    # get the market for the order
    try:
        mkt = Market.objects.get(id=mkt)
    except:
        return Response({"result": "The given market '%s' does not exist!" % mkt})
    

    # Allow POST only. 
    if request.method == 'GET':
        return Response({"result": "Please use the POST method to place a bid!"})
    
    # check the user has a market
    u = request.user
    a = m.primary_account(request.user)
    if not a:
        return Response({"result": "Please create an account for this market first!"})

    # check the POST data to the parser
    post = request.POST
    ps = mkt.parse_bid(post)
    if not ps:
        return Response({"result": "Please place a non-empty, valid bid!"})

    a.place_order(mkt, ps) 

    return Response({"result": "Got some data!", "data": request.data})


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@transaction.atomic
def api_cancel_bid(request, pk):
    """
    Cancels an outstanting, non-processed order. 

    """
    # check if the order exists
    u = request.user
    try:
        ord = Order.objects.get(account__user=u, id=pk)
    except:
        return Response({"result": "Order does not exist!"})

    # check if the order is completed
    if ord.is_processed:
        return Response({"result": "Order is already finalised!"})

    # finally, cancel the order (marks it as completed + unsuccessful)
    m = ord.account.market
    ord.cancel()
    return Response({"message": "Order successfully cancelled!"})


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_register(request, pk):
    """
    Creates an account for the market with the given id. 

    If the market does not exist or you already have an account for it, an error is returned. 
    """
    # check if any market
    if pk == "":
        return Response({"result": "Please enter the id of a market to register for!"})

    # check if market exists
    u = request.user
    try:
        mkt = Market.objects.get(id=pk)
    except:
        return Response({"result": "The given market does not exist!"})

    # check if no account for this market
    if mkt.primary_account(u):
        return Response({"result": "You already have an account for this market!"})

    # finally create the account
    mkt.create_primary_account(u)
    return Response({"result": "Account created!"})
