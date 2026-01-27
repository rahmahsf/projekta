from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeder user awal (direktur sebagai superuser)'

    def handle(self, *args, **kwargs):

        # ====== DIREKTUR (SUPERUSER) ======
        if not User.objects.filter(username='direktur').exists():
            User.objects.create_superuser(
                username='direktur',
                email='direktur@rs.com',
                password='direktur123',
                nama_lengkap='Dr. Fuad',
                role=User.Role.DIREKTUR
            )
            self.stdout.write(
                self.style.SUCCESS('Direktur (superuser) berhasil dibuat')
            )
        else:
            self.stdout.write('Direktur sudah ada')

        # ====== YANGMED ======
        if not User.objects.filter(username='yangmed').exists():
            User.objects.create_user(
                username='yangmed',
                email='yangmed@rs.com',
                password='yangmed123',
                nama_lengkap='Budi',
                role=User.Role.YANGMED,
                is_staff=True
            )
            self.stdout.write(
                self.style.SUCCESS('Yangmed berhasil dibuat')
            )

        # ====== KEPEGAWAIAN ======
        if not User.objects.filter(username='pegawai').exists():
            User.objects.create_user(
                username='pegawai',
                email='pegawai@rs.com',
                password='pegawai123',
                nama_lengkap='aldi',
                role=User.Role.KEPEGAWAIAN
            )
            self.stdout.write(
                self.style.SUCCESS('Kepegawaian berhasil dibuat')
            )
