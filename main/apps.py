from django.apps import AppConfig


class MainConfig(AppConfig):
    name = "main"

    def ready(self):
        try:
            from .scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            print(f"[ERROR] Gagal memuat scheduler: {e}")
