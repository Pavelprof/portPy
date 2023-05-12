from rest_framework import serializers
from .models import Transaction
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'asset_transaction', 'quantity_transaction','type_transaction','time_transaction')