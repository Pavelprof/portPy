from django.urls import path, include
from .views import *
from rest_framework import routers

routerPosition = routers.SimpleRouter()
routerPosition.register(r'position', PositionViewSet, basename='position')

routerAsset = routers.SimpleRouter()
routerAsset.register(r'asset', AssetViewSet)

routerTransaction = routers.SimpleRouter()
routerTransaction.register(r'transaction', TransactionViewSet)

urlpatterns = [
    path('api/v1/', include(routerPosition.urls)),
    path("api/v1/", include(routerAsset.urls)),
    path("api/v1/", include(routerTransaction.urls)),
]