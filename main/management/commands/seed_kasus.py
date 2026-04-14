from django.core.management.base import BaseCommand
from main.models import Kasus
import pandas as pd


class Command(BaseCommand):
    help = 'Seed kasus data from df_merge.csv'

    def handle(self, *args, **kwargs):
        # Clear existing data
        Kasus.objects.all().delete()
        
        # Read df_merge.csv
        try:
            df = pd.read_csv('dataset/df_merge.csv')
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('df_merge.csv not found in dataset/ directory'))
            return
        
        # Check if required columns exist
        required_columns = ['bulan', 'tahun', 'BOR', 'LOS', 'GDR']
        for col in required_columns:
            if col not in df.columns:
                self.stdout.write(self.style.ERROR(f'Column {col} not found in df_merge.csv'))
                return
        
        created_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            try:
                # Convert to appropriate types
                bulan = str(int(row['bulan'])) if pd.notna(row['bulan']) else None
                tahun = str(int(row['tahun'])) if pd.notna(row['tahun']) else None
                bor = float(row['BOR']) if pd.notna(row['BOR']) else 0.0
                los = float(row['LOS']) if pd.notna(row['LOS']) else 0.0
                gdr = float(row['GDR']) if pd.notna(row['GDR']) else 0.0
                
                # Skip if essential data is missing
                if not bulan or not tahun:
                    skipped_count += 1
                    continue
                
                # Check if record already exists
                if Kasus.objects.filter(bulan=bulan, tahun=tahun).exists():
                    skipped_count += 1
                    continue
                
                # Create Kasus record
                Kasus.objects.create(
                    bulan=bulan,
                    tahun=tahun,
                    bor=bor,
                    los=los,
                    gdr=gdr
                )
                created_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating record for bulan {row.get("bulan")}, tahun {row.get("tahun")}: {str(e)}'))
                skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {created_count} kasus records. '
                f'Skipped {skipped_count} records.'
            )
        )
