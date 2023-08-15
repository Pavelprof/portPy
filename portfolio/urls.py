from django.urls import path, include
from .views import *
from rest_framework import routers

routerPosition = routers.SimpleRouter()
routerPosition.register(r'position', PositionViewSet)

routerAsset = routers.SimpleRouter()
routerAsset.register(r'asset', AssetViewSet)

routerDeal = routers.SimpleRouter()
routerDeal.register(r'deal', DealViewSet)

routerTransaction = routers.SimpleRouter()
routerTransaction.register(r'transaction', TransactionViewSet)

urlpatterns = [
    path('api/v1/', include(routerPosition.urls)),
    path("api/v1/", include(routerAsset.urls)),
    path("api/v1/", include(routerDeal.urls)), # api/v1/deal/
    path("api/v1/", include(routerTransaction.urls)),
]