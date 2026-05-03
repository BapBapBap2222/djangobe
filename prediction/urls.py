from django.urls import path
from .views import PricePredictionView

urlpatterns = [
    path('', PricePredictionView.as_view(), name='price-prediction'),
]
