from django.core.management.base import BaseCommand
from main.models import Kasus, Rekomendasi, KasusRekomendasi
import pandas as pd


class Command(BaseCommand):
    help = 'Seed data kasus_rekomendasi dari CSV'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('dataset/df_merge.csv')

        for _, row in df.iterrows():
            kasus = Kasus.objects.get(
                bulan=row['bulan'],
                tahun=row['tahun']
            )

            for kolom in [
                'Kerja Sama',
                'Triase IGD',
                'Sistem Rujukan',
                'Alat Medis',
                'Pelatihan Dokter',
                'Kualifikasi Staf',
                'Pelayanan Pasien'
            ]:
                if row[kolom] == True:
                    rekom = Rekomendasi.objects.get(rekomendasi=kolom)

                    KasusRekomendasi.objects.get_or_create(
                        kasus=kasus,
                        rekomendasi=rekom
                    )

        self.stdout.write(self.style.SUCCESS('KasusRekomendasi berhasil di-seed'))