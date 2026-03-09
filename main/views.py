from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .services.cbr import proses_cbr
from django.contrib import messages
from django.db.models import Max,  Value
from django.core.paginator import Paginator
from main.services.indikator import hitung_indikator
from main.models import Kasus, KasusRekomendasi, Rekomendasi, RawatInap

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
    # Ambil data kasus terbaru untuk cards (selalu data terakhir)
    latest_kasus_overall = Kasus.objects.all().order_by('-tahun', '-bulan').first()
    
    # Data untuk grafik (sesuai filter)
    selected_year = request.GET.get('year', None)
    kasus_list = Kasus.objects.all().order_by('-tahun', '-bulan')
    
    # Filter berdasarkan tahun jika dipilih
    if selected_year:
        kasus_list = kasus_list.filter(tahun=selected_year)
    
    kasus_list = kasus_list[:12]
    
    # Ambil tahun-tahun yang tersedia untuk filter
    available_years = Kasus.objects.values_list('tahun', flat=True).distinct().order_by('-tahun')
    
    # Data untuk cards (selalu data terakhir)
    latest_indikator = None
    latest_status = None
    indikator_changes = None
    
    if latest_kasus_overall:
        latest_indikator = {
            'bor': latest_kasus_overall.bor,
            'los': latest_kasus_overall.los,
            'gdr': latest_kasus_overall.gdr
        }
        latest_status = evaluasi_indikator(latest_kasus_overall.bor, latest_kasus_overall.los, latest_kasus_overall.gdr)
        
        # Hitung perubahan dari bulan sebelumnya
        all_kasus_for_change = Kasus.objects.all().order_by('-tahun', '-bulan')[:2]
        if len(all_kasus_for_change) > 1:
            prev_kasus = all_kasus_for_change[1]
            indikator_changes = {
                'bor': float(latest_kasus_overall.bor) - float(prev_kasus.bor),
                'los': float(latest_kasus_overall.los) - float(prev_kasus.los),
                'gdr': float(latest_kasus_overall.gdr) - float(prev_kasus.gdr)
            }
    
    # Data untuk grafik (12 bulan terakhir)
    chart_data = {
        'labels': [],
        'bor': [],
        'los': [],
        'gdr': []
    }
    
    for kasus in kasus_list:
        # Pastikan bulan adalah integer
        bulan_int = int(kasus.bulan) if isinstance(kasus.bulan, str) else kasus.bulan
        bulan_nama = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 
                     'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'][bulan_int - 1]
        chart_data['labels'].append(f"'{bulan_nama} {kasus.tahun}'")
        chart_data['bor'].append(kasus.bor)
        chart_data['los'].append(kasus.los)
        chart_data['gdr'].append(kasus.gdr)
    
    # Data untuk tabel (5 bulan terakhir)
    table_data = []
    for kasus in kasus_list[:5]:
        # Pastikan bulan adalah integer
        bulan_int = int(kasus.bulan) if isinstance(kasus.bulan, str) else kasus.bulan
        bulan_nama = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'][bulan_int - 1]
        table_data.append({
            'bulan': bulan_nama,
            'tahun': kasus.tahun,
            'bor': kasus.bor,
            'los': kasus.los,
            'gdr': kasus.gdr,
            'status': evaluasi_indikator(kasus.bor, kasus.los, kasus.gdr)
        })
    
    # Rekomendasi dari data terakhir
    latest_rekomendasi = None
    if latest_kasus_overall:
        rekomendasi_list = KasusRekomendasi.objects.filter(kasus=latest_kasus_overall).select_related('rekomendasi')
        latest_rekomendasi = [kr.rekomendasi for kr in rekomendasi_list]
    
    # Data bulan terakhir untuk judul
    latest_month_year = None
    if latest_kasus_overall:
        bulan_int = int(latest_kasus_overall.bulan) if isinstance(latest_kasus_overall.bulan, str) else latest_kasus_overall.bulan
        bulan_nama = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'][bulan_int - 1]
        latest_month_year = f"{bulan_nama} {latest_kasus_overall.tahun}"
    
    context = {
        'latest_indikator': latest_indikator,
        'latest_status': latest_status,
        'indikator_changes': indikator_changes,
        'chart_data': chart_data,
        'table_data': table_data,
        'latest_rekomendasi': latest_rekomendasi,
        'latest_month_year': latest_month_year,
        'available_years': available_years,
        'selected_year': selected_year or available_years.first() if available_years else None,
        'page_name': 'Dashboard',
        'page_title': 'Dashboard'
    }
    
    return render(request, 'main/dashboard.html', context)

@login_required(login_url='login')
def rekomendasi(request):

    hasil = None
    indikator = None
    status = None

    if request.method == "POST":

        action = request.POST.get("action")
        # GENERATE
        if action == "generate":

            # Ambil tanggal keluar terbaru
            latest = RawatInap.objects.aggregate(
                Max("tgl_keluar")
            )["tgl_keluar__max"]

            if not latest:
                return redirect("rekomendasi")

            bulan = latest.month
            tahun = latest.year

            # Hitung indikator dari database
            indikator = hitung_indikator(bulan, tahun)

            bor = indikator["bor"]
            los = indikator["los"]
            gdr = indikator["gdr"]

            # Evaluasi status indikator
            status = evaluasi_indikator(bor, los, gdr)

            # Proses CBR
            hasil = proses_cbr(bor, los, gdr)

            # Simpan ke session untuk revise
            request.session["revise_data"] = {
                "bulan": bulan,
                "tahun": tahun,
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

        # SAVE LANGSUNG
        elif action == "save":

            data = request.session.get("revise_data")

            if not data:
                return redirect("rekomendasi")

            # Cegah duplikasi bulan
            sudah_ada = Kasus.objects.filter(
                bulan=data["bulan"],
                tahun=data["tahun"]
            ).exists()

            if sudah_ada:
                return redirect("rekomendasi")

            kasus_baru = Kasus.objects.create(
                bulan=data["bulan"],
                tahun=data["tahun"],
                bor=data["bor"],
                los=data["los"],
                gdr=data["gdr"]
            )

            # Ambil rekom dari kasus paling mirip
            kasus_lama_id = data["top_kasus"][0]["id"]

            relasi = KasusRekomendasi.objects.filter(
                kasus_id=kasus_lama_id
            )

            for r in relasi:
                KasusRekomendasi.objects.create(
                    kasus=kasus_baru,
                    rekomendasi=r.rekomendasi
                )

            del request.session["revise_data"]

            return redirect("rekomendasi")
        # MASUK REVISE
        elif action == "revise":
            return redirect("revise")

    return render(request, "main/rekomendasi.html", {
        "hasil": hasil,
        "indikator": indikator,
        "status": status,
        "page_name": "Rekomendasi",
        "page_title": "Rekomendasi"
    })

@login_required(login_url='login')
def riwayat_rekomendasi(request):

    tahun_filter = request.GET.get("tahun")

    # ambil daftar tahun unik dari database
    daftar_tahun = Kasus.objects.values_list("tahun", flat=True).distinct().order_by("-tahun")

    if tahun_filter and tahun_filter != "All":
        daftar_kasus = Kasus.objects.filter(tahun=tahun_filter).order_by("-tahun", "-bulan")
    else:
        daftar_kasus = Kasus.objects.all().order_by("-tahun", "-bulan")
    
    # Konversi ke list dan urutkan manual untuk memastikan urutan benar
    daftar_kasus_list = list(daftar_kasus)
    daftar_kasus_list.sort(key=lambda x: (int(x.tahun), int(x.bulan)), reverse=True)

    data_riwayat = []

    for k in daftar_kasus_list:
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

    paginator = Paginator(data_riwayat, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "main/riwayat-rekomendasi.html", {
        "riwayat": page_obj,
        "daftar_tahun": daftar_tahun,
        "tahun_filter": tahun_filter,
        "page_name": "Riwayat Rekomendasi",
        "page_title": "Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def revise(request):

    data = request.session.get("revise_data")

    if not data:
        return redirect("rekomendasi")

    top_kasus = data.get("top_kasus", [])

    if not top_kasus:
        return redirect("rekomendasi")

    kasus_utama_id = top_kasus[0]["id"]

    # ambil relasi rekomendasi dari kasus paling mirip
    relasi = KasusRekomendasi.objects.filter(kasus_id=kasus_utama_id)

    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]
    semua_rekomendasi = Rekomendasi.objects.all()
    # SIMPAN HASIL REVISI
    if request.method == "POST":

        dipilih = request.POST.getlist("rekomendasi")

        kasus_baru = Kasus.objects.create(
            bulan="1",
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

        return redirect("riwayat")

    # TAMPIL HALAMAN REVISE
    # Hitung status indikator
    status = evaluasi_indikator(
        data["bor"],
        data["los"],
        data["gdr"]
    )
    
    return render(request, "main/revise.html", {
        "indikator": {
            "bor": data["bor"],
            "los": data["los"],
            "gdr": data["gdr"],
        },
        "status": status,
        "top_kasus": top_kasus,
        "semua_rekomendasi": semua_rekomendasi,
        "rekomendasi_terpilih": rekomendasi_terpilih,
        "page_name": "Rekomendasi",
        "page_title": "Rekomendasi"
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
