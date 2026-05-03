from django.db import models
from django.db import connections

# Example model that could use database2
class BackupData(models.Model):
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'backup_data'  # This table would be created in database2
        app_label = 'main'

# Example of manual database usage in views/services
def get_data_from_database2():
    """
    Example function showing how to manually query database2
    """
    with connections['database2'].cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM some_table")
        count = cursor.fetchone()[0]
    return count

def write_to_database2(data):
    """
    Example function showing how to manually write to database2
    """
    with connections['database2'].cursor() as cursor:
        cursor.execute("INSERT INTO backup_data (data) VALUES (%s)", [data])
        connections['database2'].commit()
