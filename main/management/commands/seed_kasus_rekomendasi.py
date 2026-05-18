from django.core.management.base import BaseCommand
from main.models import Kasus, Rekomendasi, KasusRekomendasi
import pandas as pd


class Command(BaseCommand):
    help = 'Seed relasi kasus dan rekomendasi'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('dataset/df_merge.csv')

        kolom_rekomendasi = df.columns.difference([
            'bulan', 'tahun', 'BOR', 'LOS', 'GDR', 'Bulan_Tahun'
        ])

        for _, row in df.iterrows():
            try:
                kasus = Kasus.objects.get(
                    bulan=str(row['bulan']),
                    tahun=str(row['tahun'])
                )
            except Kasus.DoesNotExist:
                continue

            for kolom in kolom_rekomendasi:
                if str(row.get(kolom)).lower() in ['true', '1']:

                    try:
                        rekom = Rekomendasi.objects.get(rekomendasi=kolom)
                    except Rekomendasi.DoesNotExist:
                        continue

                    KasusRekomendasi.objects.get_or_create(
                        kasus=kasus,
                        rekomendasi=rekom
                    )

        self.stdout.write(self.style.SUCCESS('Seeder relasi berhasil'))