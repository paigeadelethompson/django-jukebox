from django.urls import re_path

from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    re_path(
        r'^logout/$',
        LogoutView.as_view(),
        name='logout'
    ),

    re_path(
        r'^login/$',
        LoginView.as_view(),
        dict(
            template_name='login.html'
        ),
        name='login'
    ),

    re_path(
        r'^change_password/$',
        PasswordChangeView.as_view(),
        dict(
            template_name='password_change_form.html'
        ),
        name='change_password'
    ),

    re_path(
        r'^change_password/done/$',
        PasswordChangeDoneView.as_view(),
        dict(
            template_name='password_change_done.html'
        ),
        name='password_change_done'
    ),
]
