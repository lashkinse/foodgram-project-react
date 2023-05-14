import csv
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open(
            Path(settings.DATA_FILES_DIR, "ingredients.csv"), encoding="utf-8"
        ) as file:
            reader = csv.DictReader(
                file, fieldnames=["name", "measurement_unit"]
            )
            ingredients = [
                Ingredient(
                    name=row["name"], measurement_unit=row["measurement_unit"]
                )
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients, batch_size=1000)
        self.stdout.write(self.style.SUCCESS("Ингредиенты успешно загружены"))
