from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import RawatInap
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Seed data 2026 dari file CSV ke tabel rawat_inap'

    def handle(self, *args, **kwargs):
        file_path = 'dataset/data_2026.csv'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                header = next(reader)  # Skip header
                
                with transaction.atomic():
                    for row in reader:
                        if len(row) < 17:  # Ensure we have enough columns
                            continue
                            
                        # Parse tanggal dan jam
                        tj_masuk = row[0]
                        tj_keluar = row[1]
                        no_rawat = row[2]
                        kd_kamar = row[3]
                        tgl_masuk = row[4]
                        jam_masuk = row[5]
                        tgl_keluar = row[6]
                        jam_keluar = row[7]
                        ttl_biaya = row[8]
                        stts_pulang = row[9]
                        kelas = row[10]
                        trf_kamar = row[11]
                        kd_bangsal = row[12]
                        nm_bangsal = row[13]
                        lama = row[14]
                        biaya_sekali = row[15]
                        tagihan = row[16]
                        png_jawab = row[17] if len(row) > 17 else ''
                        
                        # Parse datetime untuk tgl_masuk
                        if tgl_masuk and jam_masuk:
                            datetime_str_masuk = f"{tgl_masuk} {jam_masuk}"
                            try:
                                tgl_masuk_dt = datetime.strptime(datetime_str_masuk, "%d/%m/%Y %H:%M:%S")
                            except ValueError:
                                try:
                                    # Try alternative format
                                    tgl_masuk_dt = datetime.strptime(datetime_str_masuk, "%d/%m/%Y %H:%M")
                                except ValueError:
                                    self.stdout.write(
                                        self.style.WARNING(f'Skip row {no_rawat}: invalid tgl_masuk format')
                                    )
                                    continue
                        else:
                            tgl_masuk_dt = None
                            
                        # Parse datetime untuk tgl_keluar
                        if tgl_keluar and jam_keluar:
                            datetime_str_keluar = f"{tgl_keluar} {jam_keluar}"
                            try:
                                tgl_keluar_dt = datetime.strptime(datetime_str_keluar, "%d/%m/%Y %H:%M:%S")
                            except ValueError:
                                try:
                                    # Try alternative format
                                    tgl_keluar_dt = datetime.strptime(datetime_str_keluar, "%d/%m/%Y %H:%M")
                                except ValueError:
                                    self.stdout.write(
                                        self.style.WARNING(f'skip row {no_rawat}: invalid tgl_keluar format')
                                    )
                                    continue
                        else:
                            tgl_keluar_dt = None
                        
                        # Map status pulang
                        status_mapping = {
                            'APS': 'Atas Persetujuan Dokter',
                            'Membaik': 'Membaik',
                            'Atas Persetujuan Dokter': 'Atas Persetujuan Dokter',
                            'Meninggal': 'Meninggal'
                        }
                        stts_pulang_clean = status_mapping.get(stts_pulang, stts_pulang)
                        
                        # Create or update RawatInap record
                        RawatInap.objects.using('database2').update_or_create(
                            no_rawat=no_rawat,
                            defaults={
                                'kd_kamar': kd_kamar,
                                'tgl_masuk': tgl_masuk_dt,
                                'tgl_keluar': tgl_keluar_dt,
                                'stts_pulang': stts_pulang_clean,
                                'tempat_tidur': 65  # Default value
                            }
                        )
                        
            self.stdout.write(
                self.style.SUCCESS('Data 2026 berhasil diimport ke database2 (rs_rekom)!')
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File {file_path} tidak ditemukan')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error saat mengimport data: {str(e)}')
            )
