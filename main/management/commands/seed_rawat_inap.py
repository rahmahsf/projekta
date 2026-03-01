from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from main.models import RawatInap
import random


class Command(BaseCommand):
    help = "Seeder data dummy Rawat Inap Januari 2026"

    def handle(self, *args, **kwargs):

        for i in range(20):

            masuk = datetime(2026, 1, random.randint(1, 25))
            lama_rawat = random.randint(2, 7)
            keluar = masuk + timedelta(days=lama_rawat)

            status = random.choice([
                "Sembuh",
                "Membaik",
                "Atas Persetujuan Dokter",
                "Meninggal"
            ])

            RawatInap.objects.create(
                no_rawat=f"2026/01/{i+1:03}",
                tgl_masuk=masuk,
                tgl_keluar=keluar,
                stts_pulang=status
            )

        self.stdout.write(
            self.style.SUCCESS("Seeder Januari 2026 berhasil dijalankan")
        )