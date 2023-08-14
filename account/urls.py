from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from account.views import login_view, sign_up_view, user_block_view, user_info_view

urlpatterns = [
    path("", sign_up_view),
    path("info", user_info_view),
    path("login/", login_view),
    path("<int:user_id>/block/", user_block_view),
    path("reissue/", TokenRefreshView.as_view()),  # 토큰 재발급하기
]
