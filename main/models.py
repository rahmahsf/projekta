from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    class Role(models.TextChoices):
        DIREKTUR = 'direktur', 'Direktur'
        YANGMED = 'yangmed', 'Yangmed'
        KEPEGAWAIAN = 'kepegawaian', 'Kepegawaian'

    nama_lengkap = models.CharField(max_length=255)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

class RawatInap(models.Model):
    
    class StatusPulang(models.TextChoices):
        ATAS_PERSETUJUAN_DOKTER = 'Atas Persetujuan Dokter', 'Atas Persetujuan Dokter'
        MEMBAIK = 'Membaik', 'Membaik'
        PINDAH_KAMAR = 'Pindah Kamar', 'Pindah Kamar'
        SEMBUH = 'Sembuh', 'Sembuh'
        ATAS_PERMINTAAN_SENDIRI = 'Atas Permintaan Sendiri', 'Atas Permintaan Sendiri'
        MENINGGAL = 'Meninggal', 'Meninggal'
    
    no_rawat = models.CharField(max_length=255)
    tgl_masuk = models.DateTimeField()
    tgl_keluar = models.DateTimeField(null=True, blank=True)
    stts_pulang = models.CharField(
        max_length=50,
        choices=StatusPulang.choices,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'rawat_inap'

class Kasus(models.Model):
    bulan = models.CharField(max_length=4)
    tahun = models.CharField(max_length=5)
    bor = models.FloatField()
    los = models.FloatField()
    gdr = models.FloatField()
    
    class Meta:
        db_table = 'kasus'

class Rekomendasi(models.Model):
    
    class JenisRekomendasi(models.TextChoices):
        PELAYANAN_MEDIS = 'pelayanan medis', 'Pelayanan Medis'
        KEPEGAWAIAN = 'kepegawaian', 'Kepegawaian'
    
    rekomendasi = models.TextField()
    jenis_rekomendasi = models.CharField(
        max_length=20,
        choices=JenisRekomendasi.choices
    )
    
    class Meta:
        db_table = 'rekomendasi'
class KasusRekomendasi(models.Model):
    kasus = models.ForeignKey(
        Kasus,
        on_delete=models.CASCADE,
        db_column='id_kasus'
    )
    rekomendasi = models.ForeignKey(
        Rekomendasi,
        on_delete=models.CASCADE,
        db_column='rekomendasi_id'
    )

    class Meta:
        db_table = 'kasus_rekomendasi'
        unique_together = ('kasus', 'rekomendasi')