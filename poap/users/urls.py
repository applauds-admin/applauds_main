from django.urls import path

from poap.users.api import views

app_name = "users"
urlpatterns = [
    path("", view=views.UserRetrieveView.as_view(), name="web3-users"),
    path("nonce/<str:address>/", view=views.Web3LoginNonce.as_view(), name="web3-login"),
    path("verify/", view=views.Web3LoginVerify.as_view(), name="web3-login-verify"),
    path("me/", view=views.MeInfoView.as_view(), name="user-me"),
]
