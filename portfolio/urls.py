from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="home"),
    path("about/", about, name="about"),
    path("historical/", portfV),
    path("portfolio/", assetslV),
    path("portfolio/<slug:assetTicker>/", assetV),
    path("deals/<int:dealId>/", transV)
]