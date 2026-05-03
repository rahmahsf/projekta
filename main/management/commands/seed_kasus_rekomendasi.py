from django.core.management.base import BaseCommand
from main.models import Kasus, Rekomendasi, KasusRekomendasi
import pandas as pd


class Command(BaseCommand):
    help = 'Seed relasi kasus dan rekomendasi'

    def handle(self, *args, **kwargs):
        # Read CSV manually to handle the complex header structure
        try:
            import csv
            with open('dataset/df_merge.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                all_rows = list(reader)
                
            # First row contains the header string, split it to get column names
            header_string = all_rows[0][0]
            column_names = [col.strip() for col in header_string.split(',')]
            
            # Data rows start from index 1
            data_rows = all_rows[1:]
            
            # Create DataFrame manually
            df_data = []
            for row in data_rows:
                if len(row) >= 5:  # Ensure we have at least 5 columns
                    df_data.append({
                        'bulan': row[0].strip(),
                        'tahun': row[1].strip(), 
                        'BOR': row[2].strip(),
                        'LOS': row[3].strip(),
                        'GDR': row[4].strip()
                    })
                    # Add recommendation columns
                    for i, col_name in enumerate(column_names[5:], 5):
                        if i < len(row):
                            df_data[-1][col_name] = row[i].strip()
            
            df = pd.DataFrame(df_data)
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('df_merge.csv not found in dataset/ directory'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading df_merge.csv: {str(e)}'))
            return

        kolom_rekomendasi = df.columns.difference([
            'bulan', 'tahun', 'BOR', 'LOS', 'GDR'
        ])

        for _, row in df.iterrows():
            try:
                kasus = Kasus.objects.get(
                    bulan=row['bulan'],
                    tahun=row['tahun']
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