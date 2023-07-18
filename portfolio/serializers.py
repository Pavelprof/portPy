from rest_framework import serializers
from .models import Deal, Position
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('id', 'account', 'out_asset', 'in_asset', 'out_quantity', 'in_quantity', 'time_deal', 'note')

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('asset', 'account', 'quantity_position')