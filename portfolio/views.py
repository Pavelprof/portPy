from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from .models import *

menu = ['New asset', 'Analysis', 'Portfolio', 'Deals', 'Historical return']

def index(request):
    return render(request, 'portfolio/index.html', {'title': 'Authentification', 'menu': menu})

def about(request):
    return render(request, 'portfolio/about.html', {'title': 'About', 'menu': menu})

def portfV(request):
    return HttpResponse("Historical return")

assetsList = Asset.objects.all()

def assetslV(request):
    assetsList = Asset.objects.all()
    return render(request, 'portfolio/assetsl.html', {'title': 'Assets list', 'menu': menu, 'assetsList' : assetsList})

def assetV(request, assetTicker):
    return HttpResponse(f"<h1>Asset</h1><p>{assetTicker}</p>")

def transV(request, dealId):
    return HttpResponse(f"<h1>Deals list</h1><p>{dealId}</p>")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найденана</h1>")

# Create your views here.
