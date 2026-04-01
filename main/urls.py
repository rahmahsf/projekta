from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('', views.dashboard, name='dashboard'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('rekomendasi', views.rekomendasi, name='rekomendasi'),
    path('riwayat', views.riwayat_rekomendasi, name='riwayat'),
    path('revise', views.revise, name='revise'),
    path("detail/<int:kasus_id>/", views.detail, name="detail"),
    path("detail_revise/<int:kasus_id>/", views.detail_revise, name="detail_revise"),
    path("evaluasi/<int:kasus_id>/", views.evaluasi, name="evaluasi"),
    path('akun', views.akun, name='akun'),
    path('akun/tambah/', views.tambah_akun, name='tambah_akun'),
    path('akun/edit/<int:user_id>/', views.edit_akun, name='edit_akun'),
    path('hapus_akun/<int:user_id>/', views.hapus_akun, name='hapus_akun'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
