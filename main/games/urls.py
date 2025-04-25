"""
URL configuration for the 'games' app. Maps URLs to views for game-related actions.
"""

from django.urls import path
from django.urls import register_converter

from main.games.converters import UppercaseGameCodeConverter

from . import views

register_converter(UppercaseGameCodeConverter, 'game_code')

app_name = 'games'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('create/', views.game_create_view, name='create'),
    path('join/', views.game_join_view, name='join'),
    path('<game_code:game_code>/', views.game_detail_view, name='detail'),
    path(
        '<game_code:game_code>/start-round/',
        views.game_round_start_view,
        name='round_start',
    ),
    path(
        '<game_code:game_code>/submit-photo-caption/',
        views.photo_caption_submit_view,
        name='photo_caption_submit',
    ),
    path(
        '<game_code:game_code>/upload-photo/',
        views.photo_upload_view,
        name='photo_upload',
    ),
    path(
        '<game_code:game_code>/roasts/<str:roast_idea_id>/toggle-vote/',
        views.roast_idea_toggle_vote_view,
        name='roast_idea_toggle_vote',
    ),
]
