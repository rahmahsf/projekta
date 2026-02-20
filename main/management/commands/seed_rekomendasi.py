from django.core.management.base import BaseCommand
from main.models import Rekomendasi


class Command(BaseCommand):
    help = 'Seed data rekomendasi'

    def handle(self, *args, **kwargs):
        data = [
            ('Meningkatkan Kerja Sama dengan instansi lain', 'pelayanan medis'),
            ('Memperbaiki Triase IGD', 'pelayanan medis'),
            ('Memperbaiki Sistem Rujukan', 'pelayanan medis'),
            ('Penambahan Alat Medis', 'pelayanan medis'),
            ('Pelatihan Dokter', 'kepegawaian'),
            ('Perbaikan Kualifikasi Staf', 'kepegawaian'),
            ('Perbaikan Pelayanan Pasien', 'pelayanan medis'),
        ]

        for nama, jenis in data:
            Rekomendasi.objects.get_or_create(
                rekomendasi=nama,
                jenis_rekomendasi=jenis
            )

        self.stdout.write(self.style.SUCCESS('Data rekomendasi berhasil di-seed'))