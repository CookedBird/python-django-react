from django.urls import path

from . import views

app_name = 'bowling'
urlpatterns = [
    path('app/', views.index, name='index'),
    path('app/<int:game_id>/', views.game, name='game'),
    path('app/newgame/', views.new_game, name='newgame'),
    path('app/<int:game_id>/throw/', views.throw, name='throw'),
    path('api/games/', views.api_games, name='apigames'),
    path('api/games/<int:game_id>', views.api_games_id, name='apigamesid'),
]
