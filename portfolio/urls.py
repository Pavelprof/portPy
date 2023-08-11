from django.urls import path
from .views import *

urlpatterns = [
    path('api/v1/position/list/', PositionListApiView.as_view(), name='position'),
    path("api/v1/asset/list/", AssetAPIView.as_view()),
    path("api/v1/deal/list/", DealAPIView.as_view()),
    path("api/v1/deal/list/<int:pk>/", DealAPIUpdate.as_view()),
    path("api/v1/deal/<int:pk>/", DealAPIDetailView.as_view())
]