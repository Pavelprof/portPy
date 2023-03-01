from django.urls import path
from .views import *

urlpatterns = [
    path("", portfV),
    path("assets/<slug:assatTicker>/", assetsV),
    path("transactions/<int:transactionId>/", transV)
]