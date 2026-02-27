from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .services.cbr import proses_cbr
from django.contrib import messages
from .models import Kasus, Rekomendasi, KasusRekomendasi

# Create your views here.
User = get_user_model()  
def evaluasi_indikator(bor, los, gdr):

    hasil = {}
    # BOR
    if 60 <= bor <= 85:
        hasil["bor"] = {"status": "Ideal", "warna": "green"}
    elif bor < 60:
        hasil["bor"] = {"status": "Dibawah Ideal", "warna": "red"}
    else:
        hasil["bor"] = {"status": "Terlalu Tinggi", "warna": "red"}

    # LOS
    if 3 <= los <= 12:
        hasil["los"] = {"status": "Ideal", "warna": "green"}
    else:
        hasil["los"] = {"status": "Tidak Ideal", "warna": "red"}

    # GDR
    if gdr < 45:
        hasil["gdr"] = {"status": "Ideal", "warna": "green"}
    else:
        hasil["gdr"] = {"status": "Tidak Ideal", "warna": "red"}

    return hasil
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'main/dashboard.html')

@login_required(login_url='login')
def rekomendasi(request):

    hasil = None
    indikator = None
    status = None

    if request.method == "POST":

        action = request.POST.get("action")
        # GENERATE
        if action == "generate":

            bor = 48.0
            los = 2.9
            gdr = 2.3

            indikator = {
                "bor": bor,
                "los": los,
                "gdr": gdr
            }
            status = evaluasi_indikator(bor, los, gdr)

            hasil = proses_cbr(bor, los, gdr)

            # simpan session
            request.session["revise_data"] = {
                "bor": bor,
                "los": los,
                "gdr": gdr,
                "top_kasus": [
                    {
                        "id": k["kasus"].id,
                        "bulan": k["kasus"].bulan,
                        "tahun": k["kasus"].tahun,
                        "bor": k["kasus"].bor,
                        "los": k["kasus"].los,
                        "gdr": k["kasus"].gdr,
                        "distance": k["distance"]
                    }
                    for k in hasil["top_kasus"]
                ]
            }

        # SAVE
        elif action == "save":

            bor = float(request.POST.get("bor"))
            los = float(request.POST.get("los"))
            gdr = float(request.POST.get("gdr"))
            kasus_id = request.POST.get("kasus_id")

            kasus_baru = Kasus.objects.create(
                bulan="6",
                tahun="2026",
                bor=bor,
                los=los,
                gdr=gdr
            )

            kasus_lama = Kasus.objects.get(id=kasus_id)
            relasi = KasusRekomendasi.objects.filter(kasus=kasus_lama)

            for r in relasi:
                KasusRekomendasi.objects.create(
                    kasus=kasus_baru,
                    rekomendasi=r.rekomendasi
                )

            return redirect("rekomendasi")
        
        # REVISE
        elif action == "revise":
            return redirect("revise")
        

    return render(request, "main/rekomendasi.html", {
        "hasil": hasil,
        "indikator": indikator,
        "page_name": "Rekomendasi",
        "page_title":"Rekomendasi",
        "status": status
    })

@login_required(login_url='login')
def riwayat_rekomendasi(request):

    tahun_filter = request.GET.get("tahun")

    if tahun_filter and tahun_filter != "All":
        daftar_kasus = Kasus.objects.filter(tahun=tahun_filter).order_by("-tahun", "-bulan")
    else:
        daftar_kasus = Kasus.objects.all().order_by("-tahun", "-bulan")

    data_riwayat = []

    for k in daftar_kasus:
        relasi = KasusRekomendasi.objects.filter(kasus=k).select_related("rekomendasi")

        rekom_list = [r.rekomendasi.rekomendasi for r in relasi]

        data_riwayat.append({
            "id": k.id,
            "bulan": k.bulan,
            "tahun": k.tahun,
            "bor": k.bor,
            "los": k.los,
            "gdr": k.gdr,
            "rekomendasi": rekom_list
        })

    return render(request, "main/riwayat-rekomendasi.html", {
        "riwayat": data_riwayat,
          "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def revise(request):

    data = request.session.get("revise_data")

    if not data:
        return redirect("rekomendasi")

    top_kasus = data.get("top_kasus", [])

    # ambil rekomendasi dari kasus paling mirip (index 0)
    kasus_utama_id = top_kasus[0]["id"]
    relasi = KasusRekomendasi.objects.filter(kasus_id=kasus_utama_id)

    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]
    semua_rekomendasi = Rekomendasi.objects.all()

    return render(request, "main/revise.html", {
        "indikator": {
            "bor": data["bor"],
            "los": data["los"],
            "gdr": data["gdr"],
        },
        "top_kasus": top_kasus,
        "semua_rekomendasi": semua_rekomendasi,
        "rekomendasi_terpilih": rekomendasi_terpilih,
        "page_name": "Rekomendasi",
        "page_title":"Rekomendasi"
    })

    data = request.session.get("revise_data")

    if not data:
        return redirect("rekomendasi")

    kasus_lama = Kasus.objects.get(id=data["kasus_id"])
    relasi = KasusRekomendasi.objects.filter(kasus=kasus_lama)

    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]
    semua_rekomendasi = Rekomendasi.objects.all()

    return render(request, "main/revise.html", {
        "indikator": {
            "bor": data["bor"],
            "los": data["los"],
            "gdr": data["gdr"],
        },
        "kasus": kasus_lama,
        "distance": data.get("distance", 0),
        "semua_rekomendasi": semua_rekomendasi,
        "rekomendasi_terpilih": rekomendasi_terpilih
    })

    data = request.session.get("revise_data")

    if not data:
        return redirect("rekomendasi")

    kasus_lama = Kasus.objects.get(id=data["kasus_id"])
    relasi = KasusRekomendasi.objects.filter(kasus=kasus_lama)

    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]
    semua_rekomendasi = Rekomendasi.objects.all()

    # SIMPAN HASIL REVISI
    if request.method == "POST":

        dipilih = request.POST.getlist("rekomendasi")

        kasus_baru = Kasus.objects.create(
            bulan="6",
            tahun="2026",
            bor=data["bor"],
            los=data["los"],
            gdr=data["gdr"]
        )

        for r_id in dipilih:
            KasusRekomendasi.objects.create(
                kasus=kasus_baru,
                rekomendasi_id=r_id
            )

        del request.session["revise_data"]

        return redirect("rekomendasi")

    return render(request, "main/revise.html", {
        "indikator": data,
        "semua_rekomendasi": semua_rekomendasi,
        "rekomendasi_terpilih": rekomendasi_terpilih
    })

    kasus = Kasus.objects.get(id=kasus_id)

    semua_rekomendasi = Rekomendasi.objects.all()

    relasi = KasusRekomendasi.objects.filter(kasus=kasus)
    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]

    if request.method == "POST":

        # ambil checkbox yang dipilih
        dipilih = request.POST.getlist("rekomendasi")

        # hapus relasi lama
        KasusRekomendasi.objects.filter(kasus=kasus).delete()

        # simpan relasi baru
        for r_id in dipilih:
            KasusRekomendasi.objects.create(
                kasus=kasus,
                rekomendasi_id=r_id
            )

        return redirect("rekomendasi")

    return render(request, "main/revise.html", {
        "kasus": kasus,
        "semua_rekomendasi": semua_rekomendasi,
        "rekomendasi_terpilih": rekomendasi_terpilih
    })

@login_required(login_url='login')
def detail(request, kasus_id):

    kasus = get_object_or_404(Kasus, id=kasus_id)

    relasi = KasusRekomendasi.objects.filter(
        kasus=kasus
    ).select_related("rekomendasi")

    rekomendasi_list = [r.rekomendasi for r in relasi]
    status = evaluasi_indikator(
        kasus.bor,
        kasus.los,
        kasus.gdr
    )


    return render(request, "main/detail-data.html", {
        "kasus": kasus,
        "rekomendasi": rekomendasi_list,
        "status": status,
        "page_name": "Rekomendasi",
        "page_title":"Rekomendasi"
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
