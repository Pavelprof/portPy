from django.http import HttpResponse, HttpResponseNotFound

def index(request):
    return HttpResponse("<h1>Index</h1>")

def portfV(request):
    return HttpResponse("Historical return")

def assetsV(request, assatTicker):
    return HttpResponse(f"<h1>Assets list</h1><p>{assatTicker}</p>")

def transV(request, transactionId):
    return HttpResponse(f"<h1>Transactions list</h1><p>{transactionId}</p>")

def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")

# Create your views here.
