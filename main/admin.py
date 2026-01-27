from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nama_lengkap', 'email', 'role')
    exclude = ('first_name', 'last_name')
