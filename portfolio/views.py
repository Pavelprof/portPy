from django.http import HttpResponseNotFound
from rest_framework import generics, viewsets, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import *
from django.db.models import Q
from .serializers import *

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.filter((Q(quantity_position__gt=0) | Q(quantity_position__lt=0)) & ~Q(asset__figi=None))
    serializer_class = PositionSerializer

class AssetAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = (IsAuthenticated,)

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найденана</h1>")
