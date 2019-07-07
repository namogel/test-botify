from django.urls import path, include
from rest_framework import routers

from main.views import TownViewSet, AggregateViewSet, query

app_name = 'main'


router = routers.DefaultRouter()
router.register('towns', TownViewSet, base_name='towns')
router.register('aggs', AggregateViewSet, base_name='aggs')

urlpatterns = [
    path('', include(router.urls)),
    path('query', query),
]
