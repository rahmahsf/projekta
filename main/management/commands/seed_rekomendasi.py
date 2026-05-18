from django.core.management.base import BaseCommand
from main.models import Rekomendasi


class Command(BaseCommand):
    help = 'Seed data rekomendasi'

    def handle(self, *args, **kwargs):
        rekomendasi_data = [
            {
                "rekomendasi": "Meningkatkan kerja sama dengan instansi kesehatan lain melalui kesepakatan",
                "jenis_rekomendasi": "pelayanan medis"
            },
            {
                "rekomendasi": "Memperbaiki sistem triase IGD dengan penerapan standar prioritas kegawatdaruratan serta peningkatan kemampuan tenaga medis dalam melakukan penilaian awal",
                "jenis_rekomendasi": "pelayanan medis"
            },
            {
                "rekomendasi": "Mengoptimalkan sistem rujukan pasien dengan prosedur yang lebih sederhana agar proses lebih cepat dan efisien pada layanan rujukan pasien",
                "jenis_rekomendasi": "pelayanan medis"
            },
            {
                "rekomendasi": "Melakukan penambahan serta pemeliharaan alat medis secara berkala sesuai kebutuhan layanan dan volume pasien",
                "jenis_rekomendasi": "pelayanan medis"
            },
            {
                "rekomendasi": "Meningkatkan kompetensi dokter melalui pelatihan rutin dan pengembangan profesional berkelanjutan",
                "jenis_rekomendasi": "kepegawaian"
            },
            {
                "rekomendasi": "Memperbaiki kualifikasi dan kinerja staf melalui evaluasi berkala serta program pelatihan yang sesuai dengan kebutuhan kerja",
                "jenis_rekomendasi": "kepegawaian"
            },
            {
                "rekomendasi": "Meningkatkan kualitas pelayanan pasien dengan pendekatan yang lebih responsif, komunikatif, dan prioritaskan pada kepuasan pasien",
                "jenis_rekomendasi": "pelayanan medis"
            },
        ]

        for item in rekomendasi_data:
            Rekomendasi.objects.get_or_create(
                rekomendasi=item["rekomendasi"],
                jenis_rekomendasi=item["jenis_rekomendasi"]
            )

        self.stdout.write(
            self.style.SUCCESS('Data rekomendasi berhasil di-seed')
        )