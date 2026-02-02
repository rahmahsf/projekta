from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('rekomendasi', views.rekomendasi, name='rekomendasi'),
    path('riwayat', views.riwayat_rekomendasi, name='riwayat'),
    path('revise', views.revise, name='revise'),
    path('detail', views.detail, name='detail'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
