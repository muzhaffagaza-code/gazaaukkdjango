from django.db import models
from django.contrib.auth.models import User


class Alat(models.Model):
    nama_alat = models.CharField(max_length=100)
    kategori = models.CharField(max_length=50)
    harga_sewa = models.IntegerField()
    stok = models.IntegerField(default=1)
    foto = models.ImageField(upload_to='foto_alat/', blank=True, null=True)

    def __str__(self):
        return self.nama_alat


class Peminjaman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_peminjam = models.CharField(max_length=100, default='Umum')
    alat = models.ForeignKey(Alat, on_delete=models.CASCADE)
    lama_sewa = models.IntegerField(default=1)
    total_bayar = models.IntegerField(default=0)
    tanggal_pinjam = models.DateTimeField(auto_now_add=True)
    status_pembayaran = models.CharField(max_length=20, default='Lunas')

    def __str__(self):
        return f"{self.user.username} - {self.alat.nama_alat}"

class Profil(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('petugas', 'Petugas'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='petugas')

    def __str__(self):
        return f"{self.user.username} ({self.role})"