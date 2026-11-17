from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from .models import Alat, Peminjaman, Profil


def get_role(user):
    profil, _ = Profil.objects.get_or_create(user=user, defaults={'role': 'admin' if user.is_superuser else 'petugas'})
    return profil.role


def ke_dashboard(user):
    return redirect('admin_dashboard' if get_role(user) == 'admin' else 'petugas_dashboard')


def login_view(request):
    if request.user.is_authenticated:
        return ke_dashboard(request.user)
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            return ke_dashboard(user)
        messages.error(request, 'Username atau password salah.')
    return render(request, 'sewa/login.html')


def katalog(request):
    q = request.GET.get('q', '')
    return render(request, 'sewa/katalog.html', {'daftar_alat': Alat.objects.filter(nama_alat__icontains=q) if q else Alat.objects.all()})


def proses_pembayaran(request, alat_id):
    alat = get_object_or_404(Alat, pk=alat_id)
    if request.method == 'POST' and alat.stok > 0:
        lama = int(request.POST.get('lama_sewa', 1))
        penyewa = request.user if request.user.is_authenticated else User.objects.filter(is_superuser=True).first()
        Peminjaman.objects.create(user=penyewa, nama_peminjam=request.POST.get('nama_peminjam'), alat=alat, lama_sewa=lama, total_bayar=alat.harga_sewa * lama)
        alat.stok -= 1
        alat.save()
        return redirect('riwayat_sewa')
    return render(request, 'sewa/pembayaran.html', {'alat': alat})


def riwayat_sewa(request):
    riwayat = Peminjaman.objects.filter(user=request.user) if request.user.is_authenticated else Peminjaman.objects.all()
    return render(request, 'sewa/riwayat.html', {'riwayat': riwayat.order_by('-tanggal_pinjam')})


def data_dashboard(request):
    q_pinjam, q_alat = request.GET.get('q_pinjam', ''), request.GET.get('q_alat', '')
    peminjaman = Peminjaman.objects.all().order_by('-tanggal_pinjam')
    alat = Alat.objects.all().order_by('-id')

    if q_pinjam:
        peminjaman = peminjaman.filter(nama_peminjam__icontains=q_pinjam) | peminjaman.filter(alat__nama_alat__icontains=q_pinjam)
    if q_alat:
        alat = alat.filter(nama_alat__icontains=q_alat) | alat.filter(kategori__icontains=q_alat)

    for item in peminjaman:
        item.hari_telat = max(0, (timezone.now() - item.tanggal_pinjam).days - item.lama_sewa)
        item.estimasi_denda = item.hari_telat * 1000

    return {'semua_peminjaman': peminjaman, 'semua_alat': alat, 'total_alat': Alat.objects.count(), 'total_peminjaman': Peminjaman.objects.count(), 'q_pinjam': q_pinjam, 'q_alat': q_alat}


@login_required(login_url='login')
def admin_dashboard(request):
    return render(request, 'sewa/admin.html', data_dashboard(request)) if get_role(request.user) == 'admin' else redirect('petugas_dashboard')


@login_required(login_url='login')
def petugas_dashboard(request):
    return render(request, 'sewa/petugas.html', data_dashboard(request)) if get_role(request.user) == 'petugas' else redirect('admin_dashboard')


@login_required(login_url='login')
def tambah_alat(request):
    if get_role(request.user) != 'admin':
        return redirect('petugas_dashboard')
    if request.method == 'POST':
        Alat.objects.create(nama_alat=request.POST.get('nama_alat'), kategori=request.POST.get('kategori'), harga_sewa=request.POST.get('harga_sewa'), stok=request.POST.get('stok'), foto=request.FILES.get('foto'))
        return redirect('admin_dashboard')
    return render(request, 'sewa/tambah_alat.html')


@login_required(login_url='login')
def edit_alat(request, pk):
    alat = get_object_or_404(Alat, pk=pk)
    if request.method == 'POST':
        for field in ('nama_alat', 'kategori', 'harga_sewa', 'stok'):
            setattr(alat, field, request.POST.get(field))
        if request.FILES.get('foto'):
            alat.foto = request.FILES.get('foto')
        alat.save()
        return ke_dashboard(request.user)
    return render(request, 'sewa/edit_alat.html', {'alat': alat})


@login_required(login_url='login')
def hapus_alat(request, pk):
    get_object_or_404(Alat, pk=pk).delete()
    return ke_dashboard(request.user)


@login_required(login_url='login')
def edit_peminjaman(request, pk):
    if get_role(request.user) != 'admin':
        return redirect('petugas_dashboard')
    peminjaman = get_object_or_404(Peminjaman, pk=pk)
    if request.method == 'POST':
        alat = get_object_or_404(Alat, pk=request.POST.get('alat'))
        lama = int(request.POST.get('lama_sewa', 1))
        peminjaman.alat, peminjaman.lama_sewa, peminjaman.total_bayar = alat, lama, alat.harga_sewa * lama
        peminjaman.save()
        return redirect('admin_dashboard')
    return render(request, 'sewa/edit_peminjaman.html', {'peminjaman': peminjaman, 'daftar_alat': Alat.objects.all()})


@login_required(login_url='login')
def kembalikan_alat(request, pk):
    peminjaman = get_object_or_404(Peminjaman, pk=pk)
    telat = max(0, (timezone.now() - peminjaman.tanggal_pinjam).days - peminjaman.lama_sewa)
    peminjaman.alat.stok += 1
    peminjaman.alat.save()
    peminjaman.delete()
    messages.warning(request, f"Dikembalikan! Terlambat {telat} hari, Denda: Rp {telat * 10000:,}") if telat else messages.success(request, "Alat berhasil dikembalikan tepat waktu.")
    return ke_dashboard(request.user)


@login_required(login_url='login')
def hapus_peminjaman(request, pk):
    if get_role(request.user) == 'admin':
        get_object_or_404(Peminjaman, pk=pk).delete()
    return redirect('admin_dashboard')


def logout_view(request):
    logout(request)
    return redirect('katalog')