from django.urls import path, include
from . import views  # import your views

urlpatterns = [
    # Example
    path('profile/', views.profile_view, name='user-profile'),
]
