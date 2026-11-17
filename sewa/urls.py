from django.urls import path
from . import views

urlpatterns = [
    path('', views.katalog, name='katalog'),
    path('login/', views.login_view, name='login'),
    path('pembayaran/<int:alat_id>/', views.proses_pembayaran, name='proses_pembayaran'),
    path('riwayat/', views.riwayat_sewa, name='riwayat_sewa'),
    path('petugas-panel/', views.petugas_dashboard, name='petugas_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('tambah-alat/', views.tambah_alat, name='tambah_alat'),
    path('alat/<int:pk>/edit/', views.edit_alat, name='edit_alat'),
    path('alat/<int:pk>/hapus/', views.hapus_alat, name='hapus_alat'),
    path('peminjaman/<int:pk>/edit/', views.edit_peminjaman, name='edit_peminjaman'),
    path('peminjaman/<int:pk>/kembalikan/', views.kembalikan_alat, name='kembalikan_alat'),
    path('peminjaman/<int:pk>/hapus/', views.hapus_peminjaman, name='hapus_peminjaman'),
    path('logout/', views.logout_view, name='logout'),
]