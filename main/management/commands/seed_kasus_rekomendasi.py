from django.core.management.base import BaseCommand
from main.models import Kasus, Rekomendasi, KasusRekomendasi
import pandas as pd


class Command(BaseCommand):
    help = 'Seed data kasus_rekomendasi dari CSV'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('dataset/df_merge.csv')

        mapping_rekomendasi = {
            'Kerja Sama': 'Meningkatkan Kerja Sama dengan instansi lain',
            'Triase IGD': 'Memperbaiki Triase IGD',
            'Sistem Rujukan': 'Memperbaiki Sistem Rujukan',
            'Alat Medis': 'Penambahan Alat Medis',
            'Pelatihan Dokter': 'Pelatihan Dokter',
            'Kualifikasi Staf': 'Perbaikan Kualifikasi Staf',
            'Pelayanan Pasien': 'Perbaikan Pelayanan Pasien'
        }

        for _, row in df.iterrows():
            kasus, created = Kasus.objects.get_or_create(
                bulan=str(row['bulan']),
                tahun=str(row['tahun']),
                defaults={
                    'bor': row['BOR'],
                    'los': row['LOS'],
                    'gdr': row['GDR']
                }
            )

            for kolom, teks_rekomendasi in mapping_rekomendasi.items():
                if row[kolom] == True:
                    rekom = Rekomendasi.objects.get(rekomendasi=teks_rekomendasi)

                    KasusRekomendasi.objects.get_or_create(
                        kasus=kasus,
                        rekomendasi=rekom
                    )

        self.stdout.write(self.style.SUCCESS('KasusRekomendasi berhasil di-seed'))