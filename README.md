Cara run projek:
1. pip install django
2. pip install crispy_forms
3. pip install crispy-bootstrap5
4. sesuaikan database di setting kalau pakai mysql jalankan 'pip install pymysql'
5. buat migration
python manage.py makemigrations (optional kalau ada pilihannya pilih 1 lalu '-')
6. masukan ke database
python manage.py migrate
7. python manage.py seed_users
8. python manage.py runserver