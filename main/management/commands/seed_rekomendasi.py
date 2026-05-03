from django.core.management.base import BaseCommand
from main.models import Rekomendasi


class Command(BaseCommand):
    help = 'Seed data rekomendasi'

    def handle(self, *args, **kwargs):
        data = [
            (
                'Meningkatkan kerja sama dengan instansi kesehatan lain melalui kesepakatan',
                'pelayanan medis'
            ),
            (
                'Memperbaiki sistem triase IGD dengan penerapan standar prioritas kegawatdaruratan serta peningkatan kemampuan tenaga medis dalam melakukan penilaian awal',
                'pelayanan medis'
            ),
            (
                'Mengoptimalkan sistem rujukan pasien dengan prosedur yang lebih sederhana agar proses lebih cepat dan efisien pada layanan rujukan pasien',
                'pelayanan medis'
            ),
            (
                'Melakukan penambahan serta pemeliharaan alat medis secara berkala sesuai kebutuhan layanan dan volume pasien',
                'pelayanan medis'
            ),
            (
                'Meningkatkan kompetensi dokter melalui pelatihan rutin dan pengembangan profesional berkelanjutan',
                'kepegawaian'
            ),
            (
                'Memperbaiki kualifikasi dan kinerja staf melalui evaluasi berkala serta program pelatihan yang sesuai dengan kebutuhan kerja',
                'kepegawaian'
            ),
            (
                'Meningkatkan kualitas pelayanan pasien dengan pendekatan yang lebih responsif, komunikatif, dan prioritaskan pada kepuasan pasien',
                'pelayanan medis'
            ),
        ]

        for nama, jenis in data:
            Rekomendasi.objects.get_or_create(
                rekomendasi=nama,
                jenis_rekomendasi=jenis
            )

        self.stdout.write(self.style.SUCCESS('Data rekomendasi berhasil di-seed'))