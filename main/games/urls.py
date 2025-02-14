"""
URL configuration for the 'games' app. Maps URLs to views for game-related actions.

Routes:
- /create/: Create a new game.
- /join/: Join an existing game.
- /<game_code>/: Game lobby.
- /<game_code>/upload/: Upload a photo.
- /<game_code>/spin/: Spin the roast roulette.
- /<roast_id>/clapback/: Submit a clapback.
"""

from django.urls import path

from . import views

app_name = 'games'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('create/', views.game_create_view, name='create'),
    path('join/', views.game_join_view, name='join'),
    path('<str:game_code>/', views.game_detail_view, name='detail'),
    path('<str:game_code>/upload/', views.upload_photo_view, name='upload_photo'),
    path('<str:game_code>/spin/', views.spin_roulette_view, name='spin_roulette'),
    path(
        '<int:roast_id>/clapback/', views.submit_clapback_view, name='submit_clapback'
    ),
]
