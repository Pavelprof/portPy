from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from django.db.models import Q
from .serializers import PositionSerializer, DealSerializer

class PositionListApiView(generics.ListAPIView):
    queryset = Position.objects.filter((Q(quantity_position__gt=0) | Q(quantity_position__lt=0)) & ~Q(asset__figi=None))
    serializer_class = PositionSerializer

class AssetAPIView (APIView):
    def get(self, request):
        lst = Asset.objects.filter(id__lt=10).values()
        return Response({'assets':list(lst)})

    def post(self, request):
        asset_new = Asset.objects.create(
            ticker =request.data['ticker'],
            isin = request.data['isin'],
            figi = request.data['figi'],
            name_asset = request.data['name_asset'],
            full_name_asset = request.data['full_name_asset'],
            icon = request.data['icon'],
            currency_influence_id = request.data['currency_influence_id'],
            country_asset = request.data['country_asset'],
            type_asset = request.data['type_asset'],
            type_base_asset = request.data['type_base_asset'],
            class_code = request.data['class_code'],
            is_tradable = request.data['is_tradable']
        )
        return Response({'asset': model_to_dict(asset_new)})

class DealAPIView(generics.ListCreateAPIView):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer

class DealAPIUpdate(generics.UpdateAPIView):
    # Lazy request. Only one record, not all
    queryset = Deal.objects.all()
    serializer_class = DealSerializer

class DealAPIDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Lazy request. Only one record, not all
    queryset = Deal.objects.all()
    serializer_class = DealSerializer


# class DealAPIView(APIView):
#
#     def get(self, request):
#         dls = Deal.objects.all()
#         return Response({'deals': DealSerializer(dls, many=True).data})
#     def post(self, request):
#         deal_new = Deal.objects.create(
#             account_id =request.data['account'],
#             out_asset_id = request.data['out_asset'],
#             in_asset_id = request.data['in_asset'],
#             out_quantity = request.data['out_quantity'],
#             in_quantity = request.data['in_quantity'],
#             exchange = request.data['exchange'],
#             note = request.data['note'],
#             time_deal = request.data['time_deal']
#         )
#         return Response({'deal': model_to_dict(deal_new)})

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найденана</h1>")
