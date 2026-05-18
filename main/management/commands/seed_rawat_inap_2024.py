from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import RawatInap
import csv
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Import dataset2.csv into RawatInap table'

    def handle(self, *args, **kwargs):
        # Path ke file CSV
        csv_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'dataset', 'dataset2.csv')
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File {csv_file} tidak ditemukan!'))
            return
        
        # Baca dan import data (Tanpa menghapus data yang lama kecuali memang diinginkan)
        # self.stdout.write('Jika ingin menghapus data lama, silakan hapus komen pada baris di bawah ini')
        # with transaction.atomic():
        #     RawatInap.objects.all().delete()
        #     self.stdout.write('Data RawatInap lama telah dihapus.')
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')
            
            count = 0
            with transaction.atomic():
                for row in reader:
                    try:
                        # Parse tanggal dan jam
                        tgl_masuk_str = row['tgl_masuk']
                        jam_masuk_str = row['jam_masuk']
                        tgl_keluar_str = row['tgl_keluar']
                        jam_keluar_str = row['jam_keluar']
                        
                        # Combine date and time for tgl_masuk
                        if tgl_masuk_str and jam_masuk_str:
                            tgl_masuk = datetime.strptime(f"{tgl_masuk_str} {jam_masuk_str}", "%Y-%m-%d %H:%M:%S")
                        else:
                            continue
                        
                        # Combine date and time for tgl_keluar
                        tgl_keluar = None
                        if tgl_keluar_str and jam_keluar_str:
                            tgl_keluar = datetime.strptime(f"{tgl_keluar_str} {jam_keluar_str}", "%Y-%m-%d %H:%M:%S")
                        
                        # Map status pulang
                        stts_pulang_mapping = {
                            'APS': 'Atas Persetujuan Dokter',
                            'Membaik': 'Membaik',
                            'Atas Persetujuan Dokter': 'Atas Persetujuan Dokter',
                            'Pindah Kamar': 'Pindah Kamar',
                            'Sembuh': 'Sembuh',
                            'Atas Permintaan Sendiri': 'Atas Permintaan Sendiri',
                            'Meninggal': 'Meninggal',
                            'Lain-lain': 'Lain-lain',
                            'Rujuk': 'Rujuk',
                            'Sehat': 'Sehat'
                        }
                        
                        stts_pulang = stts_pulang_mapping.get(row['stts_pulang'], row['stts_pulang'])
                        
                        # Create RawatInap instance
                        rawat_inap = RawatInap.objects.create(
                            no_rawat=row['no_rawat'],
                            tgl_masuk=tgl_masuk,
                            tgl_keluar=tgl_keluar,
                            stts_pulang=stts_pulang,
                            tempat_tidur=65  # Default value
                        )
                        
                        count += 1
                        
                        if count % 100 == 0:
                            self.stdout.write(f'Processed {count} records...')
                            
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error processing row {count + 1}: {str(e)}'))
                        continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} records from dataset2.csv'))
