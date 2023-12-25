from django.urls import path, include
from .views import *
from rest_framework import routers

routerPosition = routers.SimpleRouter()
routerPosition.register(r'position', PositionViewSet, basename='position')

routerAsset = routers.SimpleRouter()
routerAsset.register(r'asset', AssetViewSet, basename='asset')

routerTransaction = routers.SimpleRouter()
routerTransaction.register(r'transaction', TransactionViewSet, basename='transaction')

routerAccount = routers.SimpleRouter()
routerAccount.register(r'account', AccountViewSet, basename='account')

routerStructure = routers.SimpleRouter()
routerStructure.register(r'structure', StructureViewSet, basename='structure')

urlpatterns = [
    path('api/v1/', include(routerPosition.urls)),
    # path("api/v1/", include(routerAsset.urls)),  # It's too big, should be restricted!
    path("api/v1/", include(routerTransaction.urls)),
    path("api/v1/", include(routerAccount.urls)),
    path("api/v1/", include(routerStructure.urls)),
]