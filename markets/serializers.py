from rest_framework import serializers
from markets.models import *

### Used by Django-Rest-Framework 
### to define the serialization rules for markets' elements. 

class OutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outcome
        fields = ('name',)

class EventSerializer(serializers.ModelSerializer):
    outcomes = OutcomeSerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = ('id', 'description', 'outcomes',)

class MarketSerializer(serializers.ModelSerializer):
    events = EventSerializer(required=False, many=True, read_only=True)
    class Meta:
        model = Market
        fields = ('id', 'description', 'events', 'url')

class AccountSerializer(serializers.ModelSerializer):
    # allow creation only of secondary accounts. 
    is_primary = serializers.BooleanField(read_only=True, default=False)
    class Meta:
        model = Account
        fields = ('id', 'user', 'market', 'funds', 'is_primary', 'url')

class DataSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ('id', 'market', 'description', 'is_training', 'url', )
        

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('outcome',)

class DatumSerializer(serializers.ModelSerializer):
    """
    Handles dat? serialization. 
    Makes sure dataset, set_id, and result_set are unchanged. 
    """
    set_id = serializers.IntegerField(read_only=True)
    result_set = ResultSerializer(many=True)
    data_set = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Datum
        fields = ('id', 'set_id', 'data_set', 'x', 'result_set', 'url')