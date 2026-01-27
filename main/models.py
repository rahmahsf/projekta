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
