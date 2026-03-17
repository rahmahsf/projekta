from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Kasus, RawatInap, Rekomendasi, KasusRekomendasi
from main.views import hitung_indikator, proses_cbr
from main.services.indikator import hitung_indikator_kumulatif
from datetime import datetime

class Command(BaseCommand):
    help = 'Test auto generate rekomendasi untuk bulan tertentu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bulan',
            type=int,
            help='Bulan yang ingin ditest (1-12)',
            default=2  # Default Februari
        )
        parser.add_argument(
            '--tahun',
            type=int,
            help='Tahun yang ingin ditest',
            default=2026  # Default 2026
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Jalankan simulasi tanpa menyimpan ke database'
        )

    def handle(self, *args, **options):
        bulan = options['bulan']
        tahun = options['tahun']
        dry_run = options['dry_run']

        self.stdout.write(f"=== TEST AUTO GENERATE REKOMENDASI ===")
        self.stdout.write(f"Bulan: {bulan}")
        self.stdout.write(f"Tahun: {tahun}")
        self.stdout.write(f"Mode: {'DRY RUN (simulasi)' if dry_run else 'SAVE TO DATABASE'}")
        self.stdout.write("=" * 40)

        # 1. Cek apakah data kasus sudah ada
        kasus_ada = Kasus.objects.filter(bulan=str(bulan), tahun=str(tahun)).first()
        if kasus_ada:
            self.stdout.write(
                self.style.WARNING(f"Data kasus untuk bulan {bulan}/{tahun} SUDAH ADA")
            )
            self.stdout.write(f"BOR: {kasus_ada.bor}, LOS: {kasus_ada.los}, GDR: {kasus_ada.gdr}")
            return

        # 2. Cek data RawatInap untuk bulan tersebut dan bulan sebelumnya (kumulatif)
        rawat_inap = RawatInap.objects.filter(
            tgl_keluar__month__lte=bulan,
            tgl_keluar__year=tahun
        )
        
        if not rawat_inap.exists():
            self.stdout.write(
                self.style.ERROR(f"Tidak ada data RawatInap kumulatif sampai bulan {bulan}/{tahun}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Ditemukan {rawat_inap.count()} data RawatInap kumulatif")
        )

        # 3. Hitung indikator kumulatif
        try:
            indikator = hitung_indikator_kumulatif(bulan, tahun)
            self.stdout.write("Hasil perhitungan indikator:")
            self.stdout.write(f"  BOR: {indikator['bor']}%")
            self.stdout.write(f"  LOS: {indikator['los']} hari")
            self.stdout.write(f"  GDR: {indikator['gdr']}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error hitung indikator: {e}")
            )
            return

        # 4. Proses CBR
        try:
            hasil_cbr = proses_cbr(
                indikator['bor'], 
                indikator['los'], 
                indikator['gdr']
            )
            
            rekomendasi_list = hasil_cbr.get("rekomendasi", [])
            self.stdout.write(
                self.style.SUCCESS(f"Ditemukan {len(rekomendasi_list)} rekomendasi")
            )
            
            # Tampilkan rekomendasi
            for i, rekom in enumerate(rekomendasi_list, 1):
                self.stdout.write(f"  {i}. {rekom.get('nama')} ({rekom.get('jenis')})")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error proses CBR: {e}")
            )
            return

        # 5. Simpan ke database (jika bukan dry run)
        if not dry_run:
            try:
                # Buat kasus baru
                kasus_baru = Kasus.objects.create(
                    bulan=str(bulan),
                    tahun=str(tahun),
                    bor=indikator['bor'],
                    los=indikator['los'],
                    gdr=indikator['gdr']
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Kasus baru dibuat dengan ID: {kasus_baru.id}")
                )

                # Ambil rekomendasi dari CBR dan simpan
                for rekom in hasil_cbr.get("rekomendasi", []):
                    rekom_text = rekom.get("nama")
                    
                    # Skip jika rekomendasi kosong
                    if not rekom_text or rekom_text.strip() == "":
                        continue
                    
                    # Cek apakah rekomendasi sudah ada di database
                    rekom_obj, created = Rekomendasi.objects.get_or_create(
                        rekomendasi=rekom_text,
                        defaults={
                            "jenis_rekomendasi": rekom.get("jenis", "")
                        }
                    )
                    
                    # Simpan relasi kasus-rekomendasi
                    KasusRekomendasi.objects.create(
                        kasus=kasus_baru,
                        rekomendasi=rekom_obj
                    )
                    
                    status = "Baru" if created else "Exist"
                    self.stdout.write(f"  Rekomendasi disimpan: {rekom.get('nama')} ({status})")

                self.stdout.write(
                    self.style.SUCCESS(f"✅ Data bulan {bulan}/{tahun} berhasil digenerate!")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error menyimpan ke database: {e}")
                )
        else:
            self.stdout.write(
                self.style.WARNING("Mode DRY RUN - tidak menyimpan ke database")
            )

        self.stdout.write("=" * 40)
        self.stdout.write("Test selesai!")
