from rest_framework import viewsets, generics

from markets.models import Market
from markets.serializers import MarketSerializer

# ViewSets define the view behavior.
class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer