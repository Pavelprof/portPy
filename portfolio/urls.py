from django.urls import path, include
from .views import *
from rest_framework import routers

routerPosition = routers.SimpleRouter()
routerPosition.register(r'position', DealViewSet)

routerAsset = routers.SimpleRouter()
routerAsset.register(r'asset', DealViewSet)

routerDeal = routers.SimpleRouter()
routerDeal.register(r'deal', DealViewSet)

urlpatterns = [
    path('api/v1/', include(routerPosition.urls)),
    path("api/v1/", include(routerAsset.urls)),
    path("api/v1/", include(routerDeal.urls)) # api/v1/deal/
]