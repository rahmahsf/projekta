from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .services.cbr import proses_cbr
from django.contrib import messages
from django.db.models import Max, Value, Q
from django.core.paginator import Paginator
from django.utils import timezone
from main.services.indikator import hitung_indikator
from main.models import Kasus, KasusRekomendasi, Rekomendasi, RawatInap
from functools import wraps


def role_required(*allowed_roles):
    """
    Decorator untuk memeriksa apakah user memiliki role yang diizinkan
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if request.user.role not in allowed_roles:
                messages.error(
                    request, "Anda tidak memiliki hak akses untuk halaman ini"
                )
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


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


@login_required(login_url="login")
def dashboard(request):
    # Ambil data kasus terbaru untuk cards (selalu data terakhir)
    latest_kasus_overall = Kasus.objects.all().order_by("-tahun", "-bulan").first()

    # Data untuk grafik (sesuai filter)
    selected_year = request.GET.get("year", None)
    kasus_list = Kasus.objects.all().order_by("-tahun", "-bulan")

    # Filter berdasarkan tahun jika dipilih
    if selected_year:
        kasus_list = kasus_list.filter(tahun=selected_year)

    kasus_list = kasus_list[:12]

    # Reverse order untuk grafik (terlama ke terbaru) agar data terbaru di kanan
    kasus_list = list(kasus_list)
    kasus_list.reverse()

    # Ambil tahun-tahun yang tersedia untuk filter
    available_years = (
        Kasus.objects.values_list("tahun", flat=True).distinct().order_by("-tahun")
    )

    # Data untuk cards (selalu data terakhir)
    latest_indikator = None
    latest_status = None
    indikator_changes = None

    if latest_kasus_overall:
        latest_indikator = {
            "bor": latest_kasus_overall.bor,
            "los": latest_kasus_overall.los,
            "gdr": latest_kasus_overall.gdr,
        }
        latest_status = evaluasi_indikator(
            latest_kasus_overall.bor, latest_kasus_overall.los, latest_kasus_overall.gdr
        )

        # Hitung perubahan dari bulan sebelumnya
        all_kasus_for_change = Kasus.objects.all().order_by("-tahun", "-bulan")[:2]
        if len(all_kasus_for_change) > 1:
            prev_kasus = all_kasus_for_change[1]
            indikator_changes = {
                "bor": float(latest_kasus_overall.bor) - float(prev_kasus.bor),
                "los": float(latest_kasus_overall.los) - float(prev_kasus.los),
                "gdr": float(latest_kasus_overall.gdr) - float(prev_kasus.gdr),
            }

    # Data untuk grafik (12 bulan terakhir)
    chart_data = {"labels": [], "bor": [], "los": [], "gdr": []}

    for kasus in kasus_list:
        # Pastikan bulan adalah integer
        bulan_int = int(kasus.bulan) if isinstance(kasus.bulan, str) else kasus.bulan
        bulan_nama = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "Mei",
            "Jun",
            "Jul",
            "Agu",
            "Sep",
            "Okt",
            "Nov",
            "Des",
        ][bulan_int - 1]
        chart_data["labels"].append(f"'{bulan_nama} {kasus.tahun}'")
        chart_data["bor"].append(kasus.bor)
        chart_data["los"].append(kasus.los)
        chart_data["gdr"].append(kasus.gdr)

    # Data untuk tabel (5 bulan terakhir)
    table_data = []
    for kasus in kasus_list[:5]:
        # Pastikan bulan adalah integer
        bulan_int = int(kasus.bulan) if isinstance(kasus.bulan, str) else kasus.bulan
        bulan_nama = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember",
        ][bulan_int - 1]
        table_data.append(
            {
                "bulan": bulan_nama,
                "tahun": kasus.tahun,
                "bor": kasus.bor,
                "los": kasus.los,
                "gdr": kasus.gdr,
                "status": evaluasi_indikator(kasus.bor, kasus.los, kasus.gdr),
            }
        )

    # Rekomendasi dari data terakhir
    latest_rekomendasi = None
    if latest_kasus_overall:
        rekomendasi_list = KasusRekomendasi.objects.filter(
            kasus=latest_kasus_overall
        ).select_related("rekomendasi")

        # Filter rekomendasi berdasarkan role user
        if request.user.role == "yangmed":
            latest_rekomendasi = [
                kr.rekomendasi
                for kr in rekomendasi_list
                if kr.rekomendasi.jenis_rekomendasi == "pelayanan medis"
            ]
        elif request.user.role == "kepegawaian":
            latest_rekomendasi = [
                kr.rekomendasi
                for kr in rekomendasi_list
                if kr.rekomendasi.jenis_rekomendasi == "kepegawaian"
            ]
        else:
            # Direktur bisa melihat semua rekomendasi
            latest_rekomendasi = [kr.rekomendasi for kr in rekomendasi_list]

    # Data bulan terakhir untuk judul
    latest_month_year = None
    if latest_kasus_overall:
        bulan_int = (
            int(latest_kasus_overall.bulan)
            if isinstance(latest_kasus_overall.bulan, str)
            else latest_kasus_overall.bulan
        )
        bulan_nama = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember",
        ][bulan_int - 1]
        latest_month_year = f"{bulan_nama} {latest_kasus_overall.tahun}"

    context = {
        "latest_indikator": latest_indikator,
        "latest_status": latest_status,
        "indikator_changes": indikator_changes,
        "chart_data": chart_data,
        "table_data": table_data,
        "latest_rekomendasi": latest_rekomendasi,
        "latest_month_year": latest_month_year,
        "available_years": available_years,
        "selected_year": selected_year or available_years.first()
        if available_years
        else None,
        "page_name": "Dashboard",
        "page_title": "Dashboard",
    }

    return render(request, "main/dashboard.html", context)


@login_required(login_url="login")
def rekomendasi(request):

    hasil = None
    indikator = None
    status = None

    # LOGIKA OTOMATIS: Cek data bulan ini dan bulan terlewat
    from datetime import datetime

    today = datetime.now()
    current_bulan = today.month
    current_tahun = today.year

    # Cek apakah ada data kasus untuk bulan ini
    kasus_bulan_ini = Kasus.objects.filter(
        bulan=str(current_bulan), tahun=str(current_tahun)
    ).first()

    # (Logika auto generate bulan terlewat telah dipindah ke APScheduler agar tidak memberati page load)

    if kasus_bulan_ini:
        # Tampilkan data bulan ini yang sudah ada
        indikator = {
            "bor": kasus_bulan_ini.bor,
            "los": kasus_bulan_ini.los,
            "gdr": kasus_bulan_ini.gdr,
        }

        # Evaluasi status
        status = evaluasi_indikator(
            indikator["bor"], indikator["los"], indikator["gdr"]
        )

        # Ambil rekomendasi dari kasus bulan ini
        relasi = KasusRekomendasi.objects.filter(kasus=kasus_bulan_ini).select_related(
            "rekomendasi"
        )

        # Filter rekomendasi berdasarkan role user
        rekomendasi_list = []
        if request.user.role == "yangmed":
            rekomendasi_list = [
                kr.rekomendasi
                for kr in relasi
                if kr.rekomendasi.jenis_rekomendasi == "pelayanan medis"
            ]
        elif request.user.role == "kepegawaian":
            rekomendasi_list = [
                kr.rekomendasi
                for kr in relasi
                if kr.rekomendasi.jenis_rekomendasi == "kepegawaian"
            ]
        else:
            # Direktur bisa melihat semua rekomendasi
            rekomendasi_list = [kr.rekomendasi for kr in relasi]

        # Proses CBR untuk mendapatkan kasus terdekat
        hasil_cbr = proses_cbr(kasus_bulan_ini.bor, kasus_bulan_ini.los, kasus_bulan_ini.gdr)

        # Format hasil untuk template - ambil kasus terdekat kedua (index 1)
        top_kasus_list = hasil_cbr["top_kasus"]
        if len(top_kasus_list) > 1:
            # Gunakan kasus terdekat kedua
            kasus_terdekat_kedua = top_kasus_list[1]
            hasil = {
                "rekomendasi": [
                    {"rekomendasi": r.rekomendasi, "jenis": r.jenis_rekomendasi}
                    for r in rekomendasi_list
                ],
                "top_kasus": [kasus_terdekat_kedua],
            }
        else:
            # Jika hanya ada 1 kasus, gunakan yang pertama
            hasil = {
                "rekomendasi": [
                    {"rekomendasi": r.rekomendasi, "jenis": r.jenis_rekomendasi}
                    for r in rekomendasi_list
                ],
                "top_kasus": [top_kasus_list[0]],
            }
    else:
        # Tidak ada data bulan ini, cek bulan terakhir yang ada data
        kasus_terakhir = (
            Kasus.objects.filter(tahun=str(current_tahun), bulan__lt=str(current_bulan))
            .order_by("-bulan")
            .first()
        )

        if kasus_terakhir:
            # Ada data bulan sebelumnya, tampilkan data bulan terakhir
            indikator = {
                "bor": kasus_terakhir.bor,
                "los": kasus_terakhir.los,
                "gdr": kasus_terakhir.gdr,
            }

            # Evaluasi status
            status = evaluasi_indikator(
                indikator["bor"], indikator["los"], indikator["gdr"]
            )

            # Ambil rekomendasi dari kasus terakhir
            relasi = KasusRekomendasi.objects.filter(
                kasus=kasus_terakhir
            ).select_related("rekomendasi")

            # Filter rekomendasi berdasarkan role user
            rekomendasi_list = []
            if request.user.role == "yangmed":
                rekomendasi_list = [
                    kr.rekomendasi
                    for kr in relasi
                    if kr.rekomendasi.jenis_rekomendasi == "pelayanan medis"
                ]
            elif request.user.role == "kepegawaian":
                rekomendasi_list = [
                    kr.rekomendasi
                    for kr in relasi
                    if kr.rekomendasi.jenis_rekomendasi == "kepegawaian"
                ]
            else:
                # Direktur bisa melihat semua rekomendasi
                rekomendasi_list = [kr.rekomendasi for kr in relasi]

            # Proses CBR untuk mendapatkan kasus terdekat
            hasil_cbr = proses_cbr(kasus_terakhir.bor, kasus_terakhir.los, kasus_terakhir.gdr)

            # Format hasil untuk template - ambil kasus terdekat kedua (index 1)
            top_kasus_list = hasil_cbr["top_kasus"]
            if len(top_kasus_list) > 1:
                # Gunakan kasus terdekat kedua
                kasus_terdekat_kedua = top_kasus_list[1]
                hasil = {
                    "rekomendasi": [
                        {"rekomendasi": r.rekomendasi, "jenis": r.jenis_rekomendasi}
                        for r in rekomendasi_list
                    ],
                    "top_kasus": [kasus_terdekat_kedua],
                }
            else:
                # Jika hanya ada 1 kasus, gunakan yang pertama
                hasil = {
                    "rekomendasi": [
                        {"rekomendasi": r.rekomendasi, "jenis": r.jenis_rekomendasi}
                        for r in rekomendasi_list
                    ],
                    "top_kasus": [top_kasus_list[0]],
                }
        else:
            # Tidak ada data sama sekali, tampilkan "--"
            hasil = None
            indikator = None
            status = None

    if request.method == "POST":
        action = request.POST.get("action")
        # GENERATE
        if action == "generate":
            from datetime import datetime
            
            today = datetime.now()
            target_bulan = 12 if today.month == 1 else today.month - 1
            target_tahun = today.year - 1 if today.month == 1 else today.year
            
            # Cek apakah data bulan lalu sudah ada
            sudah_ada = Kasus.objects.filter(bulan=str(target_bulan), tahun=str(target_tahun)).exists()
            
            if sudah_ada:
                messages.warning(request, "Data rekomendasi untuk bulan lalu sudah tersedia, tidak perlu generate lagi.")
                return redirect("rekomendasi")

            # Isi semua bulan yang kosong TERMASUK target_bulan (Februari) secara otomatis dan simpan ke database
            from main.services.gap_filler import fill_missing_kasus_until
            fill_missing_kasus_until(target_bulan, target_tahun)

            messages.success(request, "Berhasil generate rekomendasi untuk semua bulan yang belum tersedia.")
            return redirect("rekomendasi")

        # SAVE LANGSUNG
        elif action == "save":
            data = request.session.get("revise_data")

            if not data:
                return redirect("rekomendasi")

            # Cegah duplikasi bulan
            sudah_ada = Kasus.objects.filter(
                bulan=data["bulan"], tahun=data["tahun"]
            ).exists()

            if sudah_ada:
                return redirect("rekomendasi")

            kasus_baru = Kasus.objects.create(
                bulan=data["bulan"],
                tahun=data["tahun"],
                bor=data["bor"],
                los=data["los"],
                gdr=data["gdr"],
            )

            # Ambil rekom dari kasus paling mirip
            kasus_lama_id = data["top_kasus"][0]["id"]

            relasi = KasusRekomendasi.objects.filter(kasus_id=kasus_lama_id)

            # Filter rekomendasi berdasarkan role user
            if request.user.role == "yangmed":
                relasi = relasi.filter(rekomendasi__jenis_rekomendasi="pelayanan medis")
            elif request.user.role == "kepegawaian":
                relasi = relasi.filter(rekomendasi__jenis_rekomendasi="kepegawaian")
            # Direktur bisa melihat semua rekomendasi (tidak perlu filter)

            for r in relasi:
                KasusRekomendasi.objects.create(
                    kasus=kasus_baru, rekomendasi=r.rekomendasi
                )

            del request.session["revise_data"]

            return redirect("rekomendasi")
        # MASUK REVISE
        elif action == "revise":
            # Clear session lama dan buat baru
            if "revise_data" in request.session:
                del request.session["revise_data"]

            # Buat session data dari data yang ada
            if kasus_bulan_ini:
                # Gunakan data bulan ini
                revise_bulan = int(kasus_bulan_ini.bulan)
                revise_tahun = int(kasus_bulan_ini.tahun)
                bor = kasus_bulan_ini.bor
                los = kasus_bulan_ini.los
                gdr = kasus_bulan_ini.gdr
            elif kasus_terakhir:
                # Gunakan data bulan terakhir
                revise_bulan = int(kasus_terakhir.bulan)
                revise_tahun = int(kasus_terakhir.tahun)
                bor = kasus_terakhir.bor
                los = kasus_terakhir.los
                gdr = kasus_terakhir.gdr
            else:
                # Tidak ada data, redirect ke rekomendasi
                return redirect("rekomendasi")

            # Buat session data dengan 3 kasus terdekat
            top_kasus_data = []

            # Coba ambil 3 kasus dari bulan yang sama
            kasus_terdekat = Kasus.objects.filter(
                bulan=str(revise_bulan), tahun=str(revise_tahun)
            ).order_by("-id")[:3]  # Ambil 3 kasus terbaru

            # Jika kurang dari 3, tambahkan dari kasus terbaru lainnya
            if kasus_terdekat.count() < 3:
                # Ambil semua kasus terbaru untuk fallback
                all_kasus = Kasus.objects.all().order_by("-id")
                existing_ids = [k.id for k in kasus_terdekat]

                for k in all_kasus:
                    if len(kasus_terdekat) >= 3:
                        break
                    if k.id not in existing_ids:
                        kasus_terdekat = list(kasus_terdekat) + [k]
                        existing_ids.append(k.id)

            # Gunakan CBR service untuk perhitungan Euclidean distance yang benar

            # Proses CBR untuk mendapatkan 3 kasus terdekat dengan normalisasi
            hasil_cbr = proses_cbr(bor, los, gdr)

            # Konversi hasil CBR ke format session data - ambil kasus terdekat 2-4
            for i, k in enumerate(hasil_cbr["top_kasus"]):
                # Skip kasus terdekat pertama (index 0), ambil 2-4 (index 1-3)
                if i == 0:
                    continue
                if i > 3:  # Hanya ambil sampai index 3 (kasus ke-4)
                    break
                top_kasus_data.append(
                    {
                        "id": k["kasus"].id,
                        "bulan": k["kasus"].bulan,
                        "tahun": k["kasus"].tahun,
                        "bor": k["kasus"].bor,
                        "los": k["kasus"].los,
                        "gdr": k["kasus"].gdr,
                        "distance": k["distance"],
                    }
                )

            request.session["revise_data"] = {
                "bulan": revise_bulan,
                "tahun": revise_tahun,
                "bulan_generate": revise_bulan,
                "tahun_generate": revise_tahun,
                "bor": bor,
                "los": los,
                "gdr": gdr,
                "top_kasus": top_kasus_data,
            }

            return redirect("revise")

    # Tentukan informasi bulan yang ditampilkan
    info_bulan = None
    if kasus_bulan_ini:
        info_bulan = {
            "bulan": int(kasus_bulan_ini.bulan),
            "tahun": int(kasus_bulan_ini.tahun),
            "status": "current",
        }
    elif kasus_terakhir:
        info_bulan = {
            "bulan": int(kasus_terakhir.bulan),
            "tahun": int(kasus_terakhir.tahun),
            "status": "previous",
        }

    return render(
        request,
        "main/rekomendasi.html",
        {
            "hasil": hasil,
            "indikator": indikator,
            "status": status,
            "info_bulan": info_bulan,
            "page_name": "Rekomendasi",
            "page_title": "Rekomendasi",
        },
    )


@login_required(login_url="login")
def riwayat_rekomendasi(request):

    tahun_filter = request.GET.get("tahun")

    # ambil daftar tahun unik dari database
    daftar_tahun = (
        Kasus.objects.values_list("tahun", flat=True).distinct().order_by("-tahun")
    )

    if tahun_filter and tahun_filter != "All":
        daftar_kasus = Kasus.objects.filter(tahun=tahun_filter).order_by(
            "-tahun", "-bulan"
        )
    else:
        daftar_kasus = Kasus.objects.all().order_by("-tahun", "-bulan")

    # Konversi ke list dan urutkan manual untuk memastikan urutan benar
    daftar_kasus_list = list(daftar_kasus)
    daftar_kasus_list.sort(key=lambda x: (int(x.tahun), int(x.bulan)), reverse=True)

    data_riwayat = []

    for k in daftar_kasus_list:
        relasi = KasusRekomendasi.objects.filter(kasus=k).select_related("rekomendasi")

        # Filter rekomendasi berdasarkan role user
        if request.user.role == "yangmed":
            rekom_list = [
                r.rekomendasi.rekomendasi
                for r in relasi
                if r.rekomendasi.jenis_rekomendasi == "pelayanan medis"
            ]
        elif request.user.role == "kepegawaian":
            rekom_list = [
                r.rekomendasi.rekomendasi
                for r in relasi
                if r.rekomendasi.jenis_rekomendasi == "kepegawaian"
            ]
        else:
            # Direktur bisa melihat semua rekomendasi
            rekom_list = [r.rekomendasi.rekomendasi for r in relasi]

        data_riwayat.append(
            {
                "id": k.id,
                "bulan": k.bulan,
                "tahun": k.tahun,
                "bor": k.bor,
                "los": k.los,
                "gdr": k.gdr,
                "rekomendasi": rekom_list,
            }
        )

    paginator = Paginator(data_riwayat, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "main/riwayat-rekomendasi.html",
        {
            "riwayat": page_obj,
            "daftar_tahun": daftar_tahun,
            "tahun_filter": tahun_filter,
            "page_name": "Riwayat Rekomendasi",
            "page_title": "Riwayat Rekomendasi",
        },
    )


@login_required(login_url="login")
def revise(request):

    data = request.session.get("revise_data")

    if not data:
        return redirect("rekomendasi")

    top_kasus = data.get("top_kasus", [])

    if not top_kasus:
        return redirect("rekomendasi")

    # Ambil data kasus yang sedang direvisi

    # Ambil data kasus yang sedang direvisi
    kasus_direvisi = Kasus.objects.filter(
        bulan=str(data["bulan"]), tahun=str(data["tahun"])
    ).first()

    # Gunakan session data langsung karena sudah berisi kasus terdekat 2-4
    top_kasus_direvisi = top_kasus[:3]  # Ambil maksimal 3 kasus dari session

    kasus_utama_id = top_kasus_direvisi[0]["id"]

    # ambil relasi rekomendasi dari 3 kasus terdekat yang sudah disesuaikan
    rekomendasi_terpilih = []
    for kasus_data in top_kasus_direvisi[:3]:  # Ambil 3 kasus terdekat
        relasi = KasusRekomendasi.objects.filter(kasus_id=kasus_data["id"])
        for r in relasi:
            rekomendasi_terpilih.append(r.rekomendasi.id)

    # Ambil data kasus yang sedang direvisi (bulannya dari data["bulan"])
    kasus_direvisi = Kasus.objects.filter(
        bulan=str(data["bulan"]), tahun=str(data["tahun"])
    ).first()

    # Gunakan indikator dari kasus yang direvisi jika ada, kalau tidak pakai dari session
    if kasus_direvisi:
        indikator_data = {
            "bor": kasus_direvisi.bor,
            "los": kasus_direvisi.los,
            "gdr": kasus_direvisi.gdr,
        }
    else:
        indikator_data = {
            "bor": data["bor"],
            "los": data["los"],
            "gdr": data["gdr"],
        }

    # Filter semua rekomendasi berdasarkan role user
    if request.user.role == "yangmed":
        semua_rekomendasi = Rekomendasi.objects.filter(
            jenis_rekomendasi="pelayanan medis"
        )
    elif request.user.role == "kepegawaian":
        semua_rekomendasi = Rekomendasi.objects.filter(jenis_rekomendasi="kepegawaian")
    else:
        # Direktur bisa melihat semua rekomendasi
        semua_rekomendasi = Rekomendasi.objects.all()
    # SIMPAN HASIL REVISI
    if request.method == "POST":
        dipilih = request.POST.getlist("rekomendasi")

        kasus_baru = Kasus.objects.create(
            bulan=data["bulan"],
            tahun=data["tahun"],
            bor=data["bor"],
            los=data["los"],
            gdr=data["gdr"],
        )

        for r_id in dipilih:
            KasusRekomendasi.objects.create(kasus=kasus_baru, rekomendasi_id=r_id)

        del request.session["revise_data"]

        return redirect("riwayat")

    # TAMPIL HALAMAN REVISE
    # Hitung status indikator
    status = evaluasi_indikator(
        indikator_data["bor"], indikator_data["los"], indikator_data["gdr"]
    )

    # Jika ini dari auto generate, tampilkan bulan sebelumnya
    current_date = timezone.now()
    current_bulan = current_date.month
    current_tahun = current_date.year

    # Cek apakah ini revisi dari auto generate (bulan < current_bulan)
    if int(data["bulan"]) < current_bulan:
        status_text = "bulan terakhir yang tersedia"
    else:
        status_text = "bulan berjalan"

    info_bulan = {
        "bulan": int(data["bulan"]),
        "tahun": int(data["tahun"]),
        "status": status_text,
    }

    return render(
        request,
        "main/revise.html",
        {
            "indikator": indikator_data,
            "status": status,
            "top_kasus": top_kasus_direvisi,
            "semua_rekomendasi": semua_rekomendasi,
            "rekomendasi_terpilih": rekomendasi_terpilih,
            "info_bulan": info_bulan,
            "info_bulan_generate": {
                "bulan": int(data.get("bulan_generate", data["bulan"])),
                "tahun": int(data.get("tahun_generate", data["tahun"])),
            },
            "page_name": "Rekomendasi",
            "page_title": "Rekomendasi",
        },
    )


@login_required(login_url="login")
def detail(request, kasus_id):

    kasus = get_object_or_404(Kasus, id=kasus_id)

    relasi = KasusRekomendasi.objects.filter(kasus=kasus).select_related("rekomendasi")

    rekomendasi_list = [r.rekomendasi for r in relasi]
    status = evaluasi_indikator(kasus.bor, kasus.los, kasus.gdr)

    return render(
        request,
        "main/detail-data.html",
        {
            "kasus": kasus,
            "rekomendasi": rekomendasi_list,
            "status": status,
            "page_name": "Riwayat Rekomendasi",
            "page_title": "Riwayat Rekomendasi",
        },
    )
    
@login_required(login_url="login")
def detail_revise(request, kasus_id):

    kasus = get_object_or_404(Kasus, id=kasus_id)

    relasi = KasusRekomendasi.objects.filter(kasus=kasus).select_related("rekomendasi")

    rekomendasi_list = [r.rekomendasi for r in relasi]
    status = evaluasi_indikator(kasus.bor, kasus.los, kasus.gdr)

    return render(
        request,
        "main/detail-data-revise.html",
        {
            "kasus": kasus,
            "rekomendasi": rekomendasi_list,
            "status": status,
            "page_name": "Rekomendasi",
            "page_title": "Rekomendasi",
        },
    )


@login_required(login_url="login")
def evaluasi(request, kasus_id):
    """View untuk halaman evaluasi rekomendasi berdasarkan kasus_id"""
    
    kasus = get_object_or_404(Kasus, id=kasus_id)
    
    # Filter rekomendasi berdasarkan role user
    user_role = request.user.role
    
    # Ambil semua rekomendasi yang tersedia sesuai role
    if user_role == 'direktur':
        # Direktur lihat semua rekomendasi
        semua_rekomendasi = Rekomendasi.objects.all()
    elif user_role == 'yangmed':
        # Yangmed lihat rekomendasi jenis 'pelayanan medis'
        semua_rekomendasi = Rekomendasi.objects.filter(jenis_rekomendasi='pelayanan medis')
    elif user_role == 'kepegawaian':
        # Kepegawaian lihat rekomendasi jenis 'kepegawaian'
        semua_rekomendasi = Rekomendasi.objects.filter(jenis_rekomendasi='kepegawaian')
    else:
        # Default: tampilkan semua rekomendasi
        semua_rekomendasi = Rekomendasi.objects.all()
    
    # Ambil semua rekomendasi yang sudah terhubung dengan kasus ini
    relasi = KasusRekomendasi.objects.filter(kasus=kasus).select_related("rekomendasi")
    rekomendasi_terpilih = [r.rekomendasi.id for r in relasi]
    
    # Status indikator
    status = evaluasi_indikator(kasus.bor, kasus.los, kasus.gdr)
    
    # Info bulan
    info_bulan = {
        'bulan': int(kasus.bulan),
        'tahun': kasus.tahun,
        'status': 'Tersedia'
    }
    
    # Indikator data
    indikator = {
        'bor': kasus.bor,
        'los': kasus.los,
        'gdr': kasus.gdr
    }
    
    # Handle POST request
    if request.method == "POST":
        if request.POST.get("action") == "save":
            # Hapus semua rekomendasi lama untuk kasus ini
            KasusRekomendasi.objects.filter(kasus=kasus).delete()
            
            # Tambahkan rekomendasi baru yang dipilih
            rekomendasi_ids = request.POST.getlist("rekomendasi")
            for rec_id in rekomendasi_ids:
                rekomendasi = get_object_or_404(Rekomendasi, id=rec_id)
                KasusRekomendasi.objects.create(
                    kasus=kasus,
                    rekomendasi=rekomendasi
                )
            
            # Redirect ke detail kasus setelah menyimpan
            return redirect("detail", kasus_id=kasus.id)
    
    return render(
        request,
        "main/evaluasi.html",
        {
            "kasus": kasus,
            "info_bulan": info_bulan,
            "indikator": indikator,
            "status": status,
            "semua_rekomendasi": semua_rekomendasi,
            "rekomendasi_terpilih": rekomendasi_terpilih,
            "user_role": user_role,
            "page_name": "Evaluasi",
            "page_title": "Evaluasi Rekomendasi",
        },
    )


@role_required("direktur")
def akun(request):
    users = User.objects.all()

    return render(
        request,
        "main/kelola-akun.html",
        {"page_name": "Mengelola Akun", "page_title": "Mengelola Akun", "users": users},
    )


@role_required("direktur")
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

        # blok role direktur jika sudah ada akun direktur lain
        if role == "direktur":
            direktur_count = User.objects.filter(role="direktur").count()
            if direktur_count >= 1:
                messages.error(request, "Hanya boleh ada 1 akun direktur")
                return redirect("tambah_akun")

        # validasi username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan")
            return redirect("tambah_akun")

        # buat user
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.nama_lengkap = nama_lengkap
        user.role = role
        user.save()

        messages.success(request, "Akun berhasil ditambahkan")
        return redirect("akun")

    # Hitung jumlah akun direktur
    direktur_count = User.objects.filter(role="direktur").count()

    return render(
        request,
        "main/tambah-akun.html",
        {
            "page_name": "Mengelola Akun",
            "page_title": "Mengelola Akun",
            "direktur_count": direktur_count,
        },
    )


@role_required("direktur")
def edit_akun(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        email = request.POST.get("email")
        nama_lengkap = request.POST.get("nama_lengkap")
        role = request.POST.get("role")

        password_lama = request.POST.get("password_lama")
        password_baru = request.POST.get("password_baru")

        # Validasi proteksi role
        # 1. User non-direktur tidak bisa edit akun
        if request.user.role != "direktur":
            messages.error(request, "Hanya direktur yang dapat mengubah akun")
            return redirect("edit_akun", user_id=user.id)

        # 2. Direktur tidak bisa edit role diri sendiri
        if user.id == request.user.id:
            messages.error(request, "Direktur tidak dapat mengubah role diri sendiri")
            return redirect("edit_akun", user_id=user.id)

        # 3. Direktur tidak bisa edit role user lain yang direktur
        if user.role == "direktur":
            messages.error(request, "Akun direktur lain tidak dapat diubah role-nya")
            return redirect("edit_akun", user_id=user.id)

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

    return render(
        request,
        "main/edit-akun.html",
        {
            "page_name": "Mengelola Akun",
            "page_title": "Mengelola Akun",
            "user_edit": user,
        },
    )


@role_required("direktur")
def hapus_akun(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.role == "direktur":
        messages.error(request, "Akun direktur tidak dapat dihapus")
        return redirect("akun")

    user.delete()
    messages.success(request, "Akun berhasil dihapus")
    return redirect("akun")
