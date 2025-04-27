"""
URL configuration for the 'games' app. Maps URLs to views for game-related actions.
"""

from django.urls import path
from django.urls import register_converter

from . import views


class UppercaseGameCodeConverter:
    """
    Custom converter for game codes that ensures they are always uppercase.
    """

    regex = '[A-Za-z]{4}'  # Matches 4 letters (assuming game codes are 4 characters)

    def to_python(self, value):
        return value.upper()  # Convert to uppercase before passing to view

    def to_url(self, value):
        return value.upper()  # Ensure the URL generated is uppercase


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
        '<game_code:game_code>/roasts/<str:roast_id>/votes/',
        views.vote_create_view,
        name='vote_create',
    ),
    path(
        '<game_code:game_code>/roasts/<str:roast_id>/votes/<str:vote_id>/delete',
        views.vote_delete_view,
        name='vote_delete',
    )
]
