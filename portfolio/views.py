from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import DealSerializer

class DealAPIView(APIView):
    def get(self, request):
        lst = Deal.objects.all().values()
        return Response({'deals':list(lst)})
    def post(self, request):
        deal_new = Deal.objects.create(
            account_id =request.data['account_id'],
            out_asset_id = request.data['out_asset_id'],
            in_asset_id = request.data['in_asset_id'],
            out_quantity = request.data['out_quantity'],
            in_quantity = request.data['in_quantity'],
            lot_exchange_rate = request.data['lot_exchange_rate'],
            exchange = request.data['exchange'],
            note = request.data['note'],
            time_deal = request.data['time_deal']
        )
        return Response({'deal': model_to_dict(deal_new)})

#class TransactionAPIView(generics.ListAPIView):
#    queryset = Transaction.objects.all()
#    serializer_class = TransactionSerializer


menu = ['New asset', 'Analysis', 'Portfolio', 'Deals', 'Historical return']

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Authentification', 'menu': menu})

def about(request):
    return render(request, 'portfolio/about.html', {'title': 'About', 'menu': menu})

def portfV(request):
    return HttpResponse("Historical return")

def assetslV(request):
    assetsList = Asset.objects.all()
    return render(request, 'portfolio/assetsl.html', {'title': 'Assets list', 'menu': menu, 'assetsList' : assetsList})

def assetV(request, assetTicker):
    return HttpResponse(f"<h1>Asset</h1><p>{assetTicker}</p>")

def transV(request, dealId):
    return HttpResponse(f"<h1>Deals list</h1><p>{dealId}</p>")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найденана</h1>")
