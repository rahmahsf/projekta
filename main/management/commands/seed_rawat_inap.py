import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from main.models import RawatInap

class Command(BaseCommand):
    help = 'Seed RawatInap data from CSV file'

    def handle(self, *args, **options):
        """
        Handle the command execution
        """
        csv_file = 'dataset/data_seed.csv'
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            self.stdout.write(f"Loaded {len(df)} records from {csv_file}")
            
            # Clear existing data
            RawatInap.objects.all().delete()
            self.stdout.write("Cleared existing RawatInap data")
            
            # Counter for successful imports
            success_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Parse dates
                    tgl_masuk = pd.to_datetime(row['tgl_masuk']).date()
                    tgl_keluar = pd.to_datetime(row['tgl_keluar']).date() if pd.notna(row['tgl_keluar']) else None
                    
                    # Map status pulang to match model choices
                    stts_pulang = row['stts_pulang']
                    
                    # Get tempat_tidur from jumlah_bed column, default to 65
                    tempat_tidur = int(row['jumlah_bed']) if pd.notna(row['jumlah_bed']) else 65
                    
                    # Create RawatInap record
                    rawat_inap = RawatInap.objects.create(
                        no_rawat=str(row['no_rawat']),
                        tgl_masuk=tgl_masuk,
                        tgl_keluar=tgl_keluar,
                        stts_pulang=stts_pulang,
                        tempat_tidur=tempat_tidur
                    )
                    
                    success_count += 1
                    
                    if success_count % 100 == 0:
                        self.stdout.write(f"Processed {success_count} records...")
                        
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"Error processing row {index + 1}: {e}"))
                    self.stdout.write(f"Row data: {row.to_dict()}")
            
            self.stdout.write(self.style.SUCCESS(f"\nSeeding completed!"))
            self.stdout.write(self.style.SUCCESS(f"Successfully imported: {success_count} records"))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f"Errors: {error_count} records"))
            self.stdout.write(self.style.SUCCESS(f"Total records in database: {RawatInap.objects.count()}"))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: File {csv_file} not found!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during seeding: {e}"))
