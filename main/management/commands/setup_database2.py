from django.core.management.base import BaseCommand
from django.db import connections
from django.core.management import call_command
import pymysql

class Command(BaseCommand):
    help = 'Setup and test database2 connection'

    def handle(self, *args, **options):
        # Test connection to database2
        try:
            # Create database if it doesn't exist
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS rs_rekom")
                self.stdout.write(
                    self.style.SUCCESS('Database rs_rekom created or already exists')
                )
            connection.close()
            
            # Test Django connection to database2
            db_connection = connections['database2']
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write(
                    self.style.SUCCESS('Successfully connected to database2')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up database2: {str(e)}')
            )
            
        # Test default database connection
        try:
            default_connection = connections['default']
            with default_connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write(
                    self.style.SUCCESS('Successfully connected to default database')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error connecting to default database: {str(e)}')
            )
