import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from main.models import Kasus, KasusRekomendasi
from main.services.indikator import hitung_indikator_kumulatif
from main.services.cbr import proses_cbr
import logging

logger = logging.getLogger(__name__)


def generate_rekomendasi_otomatis():
    # Karena dijalankan terpisah dari request, kita perlu pastikan app registry Django sudah siap

    print("\n[Scheduler] Mengeksekusi Background Job: Generate Rekomendasi")

    today = datetime.now()

    # Bulan lalu
    if today.month == 1:
        target_bulan = 12
        target_tahun = today.year - 1
    else:
        target_bulan = today.month - 1
        target_tahun = today.year

    print(f"[Scheduler] Pengecekan data untuk {target_bulan}-{target_tahun}")

    # Otomatis isi kekosongan jika ada bulan-bulan sebelumnya yang belum tergenerate
    from main.services.gap_filler import fill_missing_kasus_until
    fill_missing_kasus_until(target_bulan, target_tahun)

    # Cek apakah data sudah ada
    if Kasus.objects.filter(bulan=str(target_bulan), tahun=str(target_tahun)).exists():
        print(
            f"[Scheduler] Dibatalkan: Data bulan {target_bulan}-{target_tahun} sudah di-generate sebelumnya."
        )
        return

    # Hitung indikator (kumulatif sampai akhir bulan lalu)
    try:
        indikator_terlewat = hitung_indikator_kumulatif(target_bulan, target_tahun)
    except Exception as e:
        print(f"[Scheduler] Error perhitungan indikator: {e}")
        return

    if (
        indikator_terlewat["bor"] == 0
        and indikator_terlewat["los"] == 0
        and indikator_terlewat["gdr"] == 0
    ):
        print(
            f"[Scheduler] Data indikator kosong untuk bulan {target_bulan}, tidak bisa di-generate."
        )
        return

    # Proses CBR untuk klasifikasi dan penentuan rekomendasi
    hasil_cbr = proses_cbr(
        indikator_terlewat["bor"], indikator_terlewat["los"], indikator_terlewat["gdr"]
    )

    # Simpan ke Database
    kasus_baru = Kasus.objects.create(
        bulan=str(target_bulan),
        tahun=str(target_tahun),
        bor=indikator_terlewat["bor"],
        los=indikator_terlewat["los"],
        gdr=indikator_terlewat["gdr"],
    )

    saved_rekomendasi_ids = set()
    for kasus_data in hasil_cbr.get("top_kasus", []):
        if kasus_data["kasus"].bor is not None:
            rekomendasi_dari_kasus = KasusRekomendasi.objects.filter(
                kasus=kasus_data["kasus"]
            ).select_related("rekomendasi")

            for r in rekomendasi_dari_kasus:
                if r.rekomendasi.id not in saved_rekomendasi_ids:
                    exists = KasusRekomendasi.objects.filter(
                        kasus=kasus_baru, rekomendasi=r.rekomendasi
                    ).exists()
                    if not exists:
                        KasusRekomendasi.objects.create(
                            kasus=kasus_baru, rekomendasi=r.rekomendasi
                        )
                    saved_rekomendasi_ids.add(r.rekomendasi.id)

    print(
        f"[Scheduler] Sukses! Rekomendasi untuk {target_bulan}-{target_tahun} berhasil disimpan ke database.\n"
    )


def start_scheduler():
    import sys

    # Jika berjalan dengan runserver, hanya eksekusi di worker thread (mencegah dobel)
    # Jika berjalan dengan gunicorn/production, langsung jalankan karena tidak ada reloader
    is_runserver = "runserver" in sys.argv
    if is_runserver and os.environ.get("RUN_MAIN") != "true":
        print(
            "[INFO] Menunggu proses reloader pekerja Django selesai mengatur ulang environment..."
        )
        return

    scheduler = BackgroundScheduler()

    # Eksekusi setiap hari ke-1 pukul 00:01
    scheduler.add_job(
        generate_rekomendasi_otomatis,
        trigger=CronTrigger(day="1", hour="0", minute="1"),
        id="generate_rekomendasi_bulanan",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
    print(
        "[INFO] APScheduler telah diinisialisasi. Job: 'generate_rekomendasi_bulanan' dijadwalkan tanggal 1 pukul 00:01."
    )

    atexit.register(lambda: scheduler.shutdown())
