import os
from django.urls import path, reverse_lazy
from django.contrib.auth import views
from .views import Login, Logout, AccountCreate, AccountUpdate, SearchInterest, DealUpdate

# from registrations.forms import UserActivationForm

app_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = [

    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('registration/', AccountCreate.as_view(), name='registration'),
    path('profile/<int:pk>/', AccountUpdate.as_view(), name='profile'),
    path('search/', SearchInterest.as_view(), name='search'),
    path('deal/<int:pk>/', DealUpdate.as_view(), name='deal'),

    path('password-reset/', views.PasswordResetView.as_view(success_url=reverse_lazy('auth:password_reset_done')), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('auth:password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]