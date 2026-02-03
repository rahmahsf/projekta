from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.
User = get_user_model()  
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



@login_required(login_url='login')
def akun(request):
    users = User.objects.all()

    return render(request, 'main/kelola-akun.html', {
        "page_name": "Mengelola Akun",
        "page_title": "Mengelola Akun",
        "users": users
    })

@login_required(login_url='login')
def tambah_akun(request):

    if request.method == "POST":
        email = request.POST.get("email")
        nama_lengkap = request.POST.get("nama_lengkap")
        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # validasi kosong
        if not all([email, nama_lengkap, username, password, role]):
            messages.error(request, "Semua field wajib diisi")
            return redirect("tambah_akun")

        # blok role direktur
        if role == "direktur":
            messages.error(request, "Role direktur tidak bisa ditambahkan")
            return redirect("tambah_akun")

        # validasi username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan")
            return redirect("tambah_akun")

        # buat user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.nama_lengkap = nama_lengkap
        user.role = role
        user.save()

        messages.success(request, "Akun berhasil ditambahkan")
        return redirect("akun")
    
    return render(request, 'main/tambah-akun.html', {
        "page_name": "Mengelola Akun",
        "page_title": "Mengelola Akun",
    })

@login_required(login_url='login')
def edit_akun(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        email = request.POST.get("email")
        nama_lengkap = request.POST.get("nama_lengkap")
        role = request.POST.get("role")

        password_lama = request.POST.get("password_lama")
        password_baru = request.POST.get("password_baru")

        # update data dasar
        user.email = email
        user.nama_lengkap = nama_lengkap
        user.role = role

        # LOGIKA PASSWORD
        if password_baru:
            if not password_lama:
                messages.error(request, "Password lama wajib diisi")
                return redirect("edit_akun", user_id=user.id)

            if not user.check_password(password_lama):
                messages.error(request, "Password lama salah")
                return redirect("edit_akun", user_id=user.id)

            user.set_password(password_baru)

        user.save()
        messages.success(request, "Data akun berhasil diperbarui")
        return redirect("akun")

    return render(request, "main/edit-akun.html", {
        "page_name": "Mengelola Akun",
        "page_title": "Mengelola Akun",
        "user_edit": user
    })

@login_required(login_url='login')
def hapus_akun(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.role == "direktur":
        messages.error(request, "Akun direktur tidak dapat dihapus")
        return redirect("akun")

    user.delete()
    messages.success(request, "Akun berhasil dihapus")
    return redirect("akun")
