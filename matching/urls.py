from django.urls import path
from .views import (
    handle_swipe,
    MatchViewSet,
    PotentialMatchViewSet,
)

urlpatterns = [
    # Remove the mock endpoints
    path('swipe/', handle_swipe, name='handle_swipe'),  # This will match /api/matching/swipe/
    
    # ViewSet URLs
    path('matches/', MatchViewSet.as_view({'get': 'list'}), name='match-list'),
    path('potential-matches/', PotentialMatchViewSet.as_view({'get': 'list'}), name='potential-match-list'),
]
