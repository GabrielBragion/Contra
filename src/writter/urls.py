from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

from .views import (
    create_article,
    dashboard,
    my_articles,
    update_article,
    delete_article,
    update_user,
    delete_account,
)

urlpatterns = [
    path("dashboard/", dashboard, name="writter-dashboard"),
    path("create-article/", create_article, name="create-article"),
    path("my-articles/", my_articles, name="my-articles"),
    path("update-article/<int:id>", update_article, name="update-article"),
    path("delete-article/<int:id>", delete_article, name="delete-article"),
    path("update-user/", update_user, name="update-user"),
    path("delete-account/", delete_account, name="delete-account"),
    path("change-password/", PasswordChangeView.as_view(success_url="done/"), name="change-password"),
    path("change-password/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),  
]
