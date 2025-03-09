from django.urls import path
from .views import (
    dashboard,
    browse_articles,
    subscribe_plan,
    update_user,
    create_subscription,
    cancel_subscription,
    update_subscription,
    update_subscription_result,
    #change_password,
    delete_account,
)
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView


urlpatterns = [
    path("dashboard/", dashboard, name="client-dashboard"),
    path("browse-articles/", browse_articles, name="browse-articles"),
    path("subscribe-plan/", subscribe_plan, name="subscribe-plan"),
    path("update-user/", update_user, name="client-update-user"),
    path(
        "create-subscription/<str:sub_id>/<str:plan_code>/",
        create_subscription,
        name="create-subscription",
    ),
        path(
        "cancel-subscription/<int:id>/",
        cancel_subscription,
        name="cancel-subscription",
    ),
        path(
        "update-subscription/<int:id>/",
        update_subscription,
        name="update-subscription",
    ),
    path("update-subscription-result/", update_subscription_result, name="update-subscription-result"),
    #path("change-password/", change_password, name="change-password"),
    path("change-password/", PasswordChangeView.as_view(success_url="done/"), name="change-password"),
    path("change-password/done/", PasswordChangeDoneView.as_view(), name="password_change_done"),   
    path("client-delete-account/",delete_account, name="client-delete-account")    
]
