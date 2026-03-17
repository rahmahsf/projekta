from main.models import RawatInap
import calendar

def hitung_indikator(bulan, tahun):

    tempat_tidur = 65
    periode_bulan = calendar.monthrange(tahun, bulan)[1]

    # 🔹 Filter berdasarkan TANGGAL KELUAR
    data = RawatInap.objects.filter(
        tgl_keluar__year=tahun,
        tgl_keluar__month=bulan
    )

    # TOTAL HARI PERAWATAN
    total_hari_perawatan = 0

    for d in data:
        if d.tgl_keluar and d.tgl_masuk:
            lama = (d.tgl_keluar - d.tgl_masuk).days
            total_hari_perawatan += lama

    # PASIEN KELUAR (UNIQUE)
    pasien_keluar = data.values("no_rawat").distinct().count()

    # PASIEN MENINGGAL
    pasien_meninggal = data.filter(
        stts_pulang="Meninggal"
    ).values("no_rawat").distinct().count()

    if pasien_keluar == 0:
        return {
            "bor": 0,
            "los": 0,
            "gdr": 0
        }

    # RUMUS
    bor = (total_hari_perawatan / (tempat_tidur * periode_bulan)) * 100
    los = total_hari_perawatan / pasien_keluar
    gdr = (pasien_meninggal / pasien_keluar) * 1000

    return {
        "bor": round(bor, 2),
        "los": round(los, 2),
        "gdr": round(gdr, 2)
    }

def hitung_indikator_kumulatif(bulan, tahun):
    """
    Hitung indikator kumulatif: data dari bulan 1 sampai bulan tertentu
    """
    tempat_tidur = 65
    periode_bulan = calendar.monthrange(tahun, bulan)[1]

    # 🔹 Filter data KUMULATIF: bulan 1 sampai bulan tertentu
    data = RawatInap.objects.filter(
        tgl_keluar__year=tahun,
        tgl_keluar__month__lte=bulan  # <= bulan tertentu
    )

    # TOTAL HARI PERAWATAN
    total_hari_perawatan = 0

    for d in data:
        if d.tgl_keluar and d.tgl_masuk:
            lama = (d.tgl_keluar - d.tgl_masuk).days
            total_hari_perawatan += lama

    # PASIEN KELUAR (UNIQUE)
    pasien_keluar = data.values("no_rawat").distinct().count()

    # PASIEN MENINGGAL
    pasien_meninggal = data.filter(
        stts_pulang="Meninggal"
    ).values("no_rawat").distinct().count()

    if pasien_keluar == 0:
        return {
            "bor": 0,
            "los": 0,
            "gdr": 0
        }

    # RUMUS (sama dengan fungsi biasa)
    bor = (total_hari_perawatan / (tempat_tidur * periode_bulan)) * 100
    los = total_hari_perawatan / pasien_keluar
    gdr = (pasien_meninggal / pasien_keluar) * 1000

    return {
        "bor": round(bor, 2),
        "los": round(los, 2),
        "gdr": round(gdr, 2)
    }