from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run all specific seed commands'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting seed_all process...')
        
        # Daftar command seed yang ingin dijalankan secara berurutan
        seed_commands = [
            'seed_users',
            'seed_kasus',
            'seed_rawat_inap_2024',
            'seed_rawat_inap',
            'seed_data2026',
            'seed_rekomendasi',
            'seed_kasus_rekomendasi'
        ]
        for command_name in seed_commands:
            self.stdout.write(self.style.WARNING(f'\n--- Running: {command_name} ---'))
            try:
                call_command(command_name)
                self.stdout.write(self.style.SUCCESS(f'Successfully ran {command_name}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running {command_name}: {str(e)}'))
                
        self.stdout.write(self.style.SUCCESS('\nAll seed commands executed!'))
