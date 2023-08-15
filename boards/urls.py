from django.urls import path

from boards.views import post_board_view

urlpatterns = [
    path('', post_board_view),
]