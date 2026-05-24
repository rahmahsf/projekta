from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Mengosongkan semua data di database default & database2 lalu menjalankan seed_all secara otomatis'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Memulai proses reset database...'))
        
        # 1. Flush database default (rs_pku)
        self.stdout.write('Membersihkan database default (rs_pku)...')
        try:
            call_command('flush', interactive=False, database='default')
            self.stdout.write(self.style.SUCCESS('Database default berhasil dikosongkan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Gagal mengosongkan database default: {str(e)}'))

        # 2. Flush database2 (rs_rekom)
        self.stdout.write('Membersihkan database2 (rs_rekom)...')
        try:
            call_command('flush', interactive=False, database='database2')
            self.stdout.write(self.style.SUCCESS('Database2 berhasil dikosongkan.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Gagal mengosongkan database2: {str(e)}'))

        # 3. Jalankan seed_all
        self.stdout.write(self.style.WARNING('\nMemulai proses seeding ulang data...'))
        try:
            call_command('seed_all')
            self.stdout.write(self.style.SUCCESS('\nSemua proses reset dan seeding selesai dengan sukses!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Gagal menjalankan seeding: {str(e)}'))
