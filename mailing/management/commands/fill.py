from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    """Команда для заполнения БД фикстурой data.json"""
    def handle(self, *args, **options):
        call_command('loaddata', 'data.json')
