from rest_framework import viewsets, generics, mixins

from markets.models import Market, Account, DataSet
from markets.serializers import *
from rest_framework.response import Response
from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view, detail_route
from django.shortcuts import get_object_or_404
from rest_framework.reverse import reverse
from rest_framework.permissions import IsAuthenticated

### Used by Django-Rest-Framework 
### defines the API views for markets' elements. 

class PlayViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )
    def list(self, request):
        return Response({
            "bid": reverse('api_bid', kwargs={'mkt':''}, request=request),
            "cancel_bid": reverse('api_cancel_bid', kwargs={'pk':''}, request=request),
            "register": reverse('api_register', kwargs={'pk':''}, request=request),
            })


class MarketViewSet(viewsets.ModelViewSet):
    """
    This view lists all active markets and allows creation of new ones. 
    """
    queryset = Market.objects.all()
    serializer_class = MarketSerializer

    def get_queryset(self):
        if not self.request.user:
            return Market.objects.none()
        else:
            return Market.objects.all()

class AccountViewSet(viewsets.ModelViewSet):
    """
    This view allows listing and editing the accounts associated with a user.
    """
    queryset = Account.objects.none()
    serializer_class = AccountSerializer

    def get_queryset(self):
        if not self.request.user:
            return Account.objects.none()
        else:
            return Account.objects.filter(user=self.request.user)


class DataSetViewSet(viewsets.ModelViewSet):
    """
    This view allows listing and editing of the datasets registered for markets. 
    """
    queryset = DataSet.objects.all()
    serializer_class = DataSetSerializer

    @detail_route(methods=['post'])
    def random_data(self, request, pk=None):
        set = get_object_or_404(queryset, pk=pk)
        serializer = PasswordSerializer(data=request.data)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class DatumViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    This view lists all data with market results and allows for its creation and modification. 
    To delete a datum you must currently delete the whole set. 
    """
    queryset = Datum.objects.all()
    serializer_class = DatumSerializer
    
