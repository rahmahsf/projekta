from django.core.management.base import BaseCommand
from main.models import User, Rekomendasi, RawatInap

class Command(BaseCommand):
    help = 'Verify all seeding data in both databases'

    def handle(self, *args, **options):
        self.stdout.write("=== Verifikasi Data Seeding ===")
        
        # Check Users in default database (rs_pku)
        users = User.objects.all()
        self.stdout.write(f"\n👥 Users di rs_pku: {users.count()}")
        for user in users:
            self.stdout.write(f"   - {user.username} ({user.role})")
        
        # Check Rekomendasi in default database (rs_pku)
        rekomendasi = Rekomendasi.objects.all()
        self.stdout.write(f"\n💡 Rekomendasi di rs_pku: {rekomendasi.count()}")
        for rek in rekomendasi:
            self.stdout.write(f"   - {rek.jenis_rekomendasi}: {rek.rekomendasi[:50]}...")
        
        # Check RawatInap in database2 (rs_rekom)
        rawat_inap = RawatInap.objects.using('database2').all()
        self.stdout.write(f"\n🏥 RawatInap di rs_rekom: {rawat_inap.count()}")
        
        # Summary
        self.stdout.write("\n=== Summary ===")
        self.stdout.write(f"✅ Users: {users.count()} records")
        self.stdout.write(f"✅ Rekomendasi: {rekomendasi.count()} records") 
        self.stdout.write(f"✅ RawatInap: {rawat_inap.count()} records")
        
        if users.count() >= 4 and rekomendasi.count() >= 5:
            self.stdout.write(self.style.SUCCESS("✨ Semua seeding berhasil!"))
        else:
            self.stdout.write(self.style.WARNING("⚠️ Beberapa data mungkin belum lengkap"))
