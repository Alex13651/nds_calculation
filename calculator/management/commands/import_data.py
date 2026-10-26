from django.core.management.base import BaseCommand
from calculator.models import Country
from calculator.vat_data import COUNTRIES, ISO_CODES

class Command(BaseCommand):
    help = 'Импорт стран из vat_data.py в базу данных'

    def handle(self, *args, **kwargs):
        count = 0
        for ru, data in COUNTRIES.items():
            if not Country.objects.filter(name_ru=ru).exists():
                Country.objects.create(
                    name_ru=ru,
                    name_en=data['en'],
                    rate=data['rate'],
                    note=data['note'],
                    scope=data['scope'],
                    iso_code=ISO_CODES.get(ru, ''),
                    future=data.get('future', False)
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Успешно импортировано стран: {count}'))