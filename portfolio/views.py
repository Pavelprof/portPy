from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets
from rest_framework.response import Response

from django.db.models import Q

from .permissions import isAdminOrReadOnly, IsOwner
from .serializers import *
from .utils import fetch_prices_and_currencies

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.filter(Q(quantity_position__gt=0) | Q(quantity_position__lt=0))
    serializer_class = PositionSerializer
    permission_classes = (IsOwner,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        assets = set(position.asset for position in queryset)
        prices_and_currencies = fetch_prices_and_currencies(assets)

        serializer = self.get_serializer(queryset, many=True, context={'prices_and_currencies': prices_and_currencies})
        return Response(serializer.data)

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (isAdminOrReadOnly,)

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = (IsOwner,)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsOwner,)

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найденана</h1>")
