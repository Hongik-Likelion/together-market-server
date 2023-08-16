from django.urls import path

from boards.views import post_board_view, single_board_view, board_like_view, board_unlike_view

urlpatterns = [
    path('', post_board_view),
    path('<int:board_id>/', single_board_view),
    path('<int:board_id>/like', board_like_view),
    path('<int:board_id>/unlike', board_unlike_view),
]