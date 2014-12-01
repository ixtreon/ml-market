from rest_framework import serializers
from markets.models import Market, Event

class MarketSerializer(serializers.ModelSerializer):
    events = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Market
        fields = ('description', 'pub_date', 'events')


class EventSerializer(serializers.ModelSerializer):
    outcomes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Event
        fields = ('description', 'pub_date', 'outcomes')
