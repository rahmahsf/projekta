from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from main.models import RawatInap
import random


class Command(BaseCommand):
    help = "Seeder data dummy Rawat Inap untuk bulan Januari-Maret 2026"

    def handle(self, *args, **kwargs):
        self.stdout.write("=== SEED DATA RAWAT INAP JANUARI-MARET 2026 ===")
        
        # Data per bulan
        data_bulan = {
            1: 20,  
            2: 20, 
            3: 5   
        }
        
        for bulan, jumlah in data_bulan.items():
            # Hapus data lama untuk bulan ini dari database2
            RawatInap.objects.using('database2').filter(
                tgl_keluar__month=bulan,
                tgl_keluar__year=2026
            ).delete()
            
            # Nama bulan
            nama_bulan = {
                1: "Januari",
                2: "Februari", 
                3: "Maret"
            }
            
            self.stdout.write(f"\nMembuat data {nama_bulan[bulan]} 2026 ({jumlah} data)...")
            
            for i in range(jumlah):
                masuk = datetime(2026, bulan, random.randint(1, 25))
                lama_rawat = random.randint(2,7)
                keluar = masuk + timedelta(days=lama_rawat)

                status = random.choice([
                    "Sembuh",
                    "Membaik",
                    "Atas Persetujuan Dokter",
                    "Meninggal"
                ])

                RawatInap.objects.using('database2').create(
                    no_rawat=f"2026/{bulan:02d}/{i+1:03}",
                    tgl_masuk=masuk,
                    tgl_keluar=keluar,
                    stts_pulang=status
                )
        
        self.stdout.write("\n Data dummy Januari-Maret 2026 berhasil dibuat ke database2 (rs_rekom)!")
        self.stdout.write("  - Januari: 20 data")
        self.stdout.write("  - Februari: 20 data") 
        self.stdout.write("  - Maret: 5 data")
        self.stdout.write("=== SELESAI ===")