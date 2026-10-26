from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/compare/', views.api_compare, name='api_compare'),
    path('api/distribution/', views.api_distribution, name='api_distribution'),
    path('api/map_data/', views.api_map_data, name='api_map_data'),
]