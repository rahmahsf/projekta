from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'main/dashboard.html')

@login_required(login_url='login')
def rekomendasi(request):
    return render(request, "main/rekomendasi.html", {
        "page_name": "Rekomendasi",
        "page_title": "Rekomendasi"
    })

@login_required(login_url='login')
def riwayat_rekomendasi(request):
    return render(request, 'main/riwayat-rekomendasi.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def revise(request):
    return render(request, 'main/revise.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def detail(request):
    return render(request, 'main/detail-data.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

User = get_user_model()   # ⬅️ INI KUNCI UTAMA

@login_required(login_url='login')
def akun(request):
    users = User.objects.all()

    return render(request, 'main/kelola-akun.html', {
        "page_name": "Mengelola Akun",
        "page_title": "Mengelola Akun",
        "users": users
    })

User = get_user_model()

@login_required(login_url='login')
def tambah_akun(request):
    if request.method == "POST":
        email = request.POST.get("email")
        nama = request.POST.get("nama_lengkap")
        username = request.POST.get("username")
        password = request.POST.get("password")

        # validasi sederhana
        if not all([email, nama, username, password]):
            messages.error(request, "Semua field wajib diisi.")
            return redirect("tambah_akun")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan.")
            return redirect("tambah_akun")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # kalau kamu punya field nama lengkap
        user.nama_lengkap = nama
        user.save()

        messages.success(request, "Akun berhasil ditambahkan.")
        return redirect("akun")  # balik ke list akun

    return render(request, "main/tambah-akun.html", {
        "page_name": "Kelola Akun",
        "page_title": "Tambah Akun"
    })
