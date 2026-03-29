from django.db.models import Q
from main.models import Kasus, KasusRekomendasi, RawatInap, Rekomendasi
from main.services.indikator import hitung_indikator
from main.services.cbr import proses_cbr


def fill_missing_kasus_until(target_bulan, target_tahun):
    """
    Mencari semua bulan yang memiliki data RawatInap namun belum ada Kasus-nya,
    dari kapanpun hingga target_bulan/target_tahun (inclusive).
    Mendukung lintas tahun (contoh: Des 2025 → Jan 2026 → Feb 2026).

    Pendekatan: ambil tgl_keluar mentah lalu ekstrak (year, month) di Python
    untuk menghindari masalah ORM values_list + distinct + order_by di MySQL.
    """

    # Ambil semua tgl_keluar yang tidak null, sebelum atau sama dengan target
    raw_dates = (
        RawatInap.objects.filter(
            tgl_keluar__isnull=False,
        )
        .filter(
            Q(tgl_keluar__year__lt=target_tahun)
            | Q(tgl_keluar__year=target_tahun, tgl_keluar__month__lte=target_bulan)
        )
        .values_list("tgl_keluar", flat=True)
        .order_by("tgl_keluar")
    )

    # Ekstrasi (year, month) unik secara kronologis di Python (aman dari quirk ORM)
    seen = set()
    sorted_dates = []
    for d in raw_dates:
        if d is None:
            continue
        key = (d.year, d.month)
        if key not in seen:
            seen.add(key)
            sorted_dates.append(key)

    # sorted_dates sudah terurut karena raw_dates di-order_by("tgl_keluar")

    for tahun, bulan in sorted_dates:
        # Sudah ada di database? Lewati.
        if Kasus.objects.filter(bulan=str(bulan), tahun=str(tahun)).exists():
            continue

        # Hitung indikator untuk bulan spesifik ini
        try:
            indikator_terlewat = hitung_indikator(bulan, tahun)
        except Exception:
            continue

        if (
            indikator_terlewat["bor"] == 0
            and indikator_terlewat["los"] == 0
            and indikator_terlewat["gdr"] == 0
        ):
            # Tidak ada data pasien yang bisa dihitung, lewati
            continue

        # Jalankan CBR dengan nilai indikator bulan ini
        hasil_cbr = proses_cbr(
            indikator_terlewat["bor"],
            indikator_terlewat["los"],
            indikator_terlewat["gdr"],
        )

        # Buat Kasus baru untuk bulan yang kosong ini
        kasus_baru = Kasus.objects.create(
            bulan=str(bulan),
            tahun=str(tahun),
            bor=indikator_terlewat["bor"],
            los=indikator_terlewat["los"],
            gdr=indikator_terlewat["gdr"],
        )

        # Tentukan bulan sebelumnya (aman lintas tahun: Des → bulan sebelumnya = Nov tahun sama, Jan → Des tahun sebelumnya)
        prev_b = bulan - 1
        prev_t = tahun
        if prev_b < 1:
            prev_b = 12
            prev_t = tahun - 1

        all_rekomendasi = []

        # Prioritas 1: Warisi rekomendasi dari Kasus bulan sebelumnya (estafet)
        kasus_bulan_sebelumnya = Kasus.objects.filter(
            bulan=str(prev_b), tahun=str(prev_t)
        ).first()

        if kasus_bulan_sebelumnya:
            rekomendasi_dari_kasus = KasusRekomendasi.objects.filter(
                kasus=kasus_bulan_sebelumnya
            ).select_related("rekomendasi")

            for r in rekomendasi_dari_kasus:
                all_rekomendasi.append(
                    {
                        "rekomendasi": r.rekomendasi.rekomendasi,
                        "jenis": r.rekomendasi.jenis_rekomendasi,
                    }
                )

        # Prioritas 2: Gunakan hasil CBR murni jika tidak ada warisan dari bulan sebelumnya
        if not all_rekomendasi:
            for kasus_data in hasil_cbr.get("top_kasus", []):
                if (
                    kasus_data["kasus"].bor is not None
                    and kasus_data["kasus"].los is not None
                    and kasus_data["kasus"].gdr is not None
                ):
                    rekomendasi_dari_kasus = KasusRekomendasi.objects.filter(
                        kasus=kasus_data["kasus"]
                    ).select_related("rekomendasi")

                    for r in rekomendasi_dari_kasus:
                        all_rekomendasi.append(
                            {
                                "rekomendasi": r.rekomendasi.rekomendasi,
                                "jenis": r.rekomendasi.jenis_rekomendasi,
                            }
                        )

        # Simpan seluruh rekomendasi tanpa duplikat
        saved_rekomendasi_ids = set()
        for rekom in all_rekomendasi:
            rekom_text = rekom["rekomendasi"]
            if not rekom_text or rekom_text.strip() == "":
                continue

            rekom_obj, _ = Rekomendasi.objects.get_or_create(
                rekomendasi=rekom_text,
                defaults={"jenis_rekomendasi": rekom.get("jenis", "")},
            )

            if rekom_obj.id not in saved_rekomendasi_ids:
                if not KasusRekomendasi.objects.filter(
                    kasus=kasus_baru, rekomendasi=rekom_obj
                ).exists():
                    KasusRekomendasi.objects.create(
                        kasus=kasus_baru, rekomendasi=rekom_obj
                    )
                    saved_rekomendasi_ids.add(rekom_obj.id)
