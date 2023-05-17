from rest_framework import serializers
from .models import Deal
class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ('id', 'account', 'out_asset', 'in_asset', 'out_quantity', 'in_quantity', 'time_deal', 'note')