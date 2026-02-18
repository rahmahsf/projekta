from django.core.management.base import BaseCommand
from main.models import Rekomendasi


class Command(BaseCommand):
    help = 'Seed data rekomendasi'

    def handle(self, *args, **kwargs):
        data = [
            ('Kerja Sama', 'pelayanan medis'),
            ('Triase IGD', 'pelayanan medis'),
            ('Sistem Rujukan', 'pelayanan medis'),
            ('Alat Medis', 'pelayanan medis'),
            ('Pelatihan Dokter', 'kepegawaian'),
            ('Kualifikasi Staf', 'kepegawaian'),
            ('Pelayanan Pasien', 'pelayanan medis'),
        ]

        for nama, jenis in data:
            Rekomendasi.objects.get_or_create(
                rekomendasi=nama,
                jenis_rekomendasi=jenis
            )

        self.stdout.write(self.style.SUCCESS('Data rekomendasi berhasil di-seed'))