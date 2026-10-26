from django.db import models

class Country(models.Model):
    name_ru = models.CharField(max_length=100, unique=True, verbose_name="Название (рус)")
    name_en = models.CharField(max_length=100, verbose_name="Название (англ)")
    rate = models.FloatField(null=True, blank=True, verbose_name="Ставка НДС (%)")
    note = models.TextField(blank=True, verbose_name="Примечание")
    scope = models.TextField(blank=True, verbose_name="Области применения")
    iso_code = models.CharField(max_length=3, blank=True, verbose_name="ISO код")
    future = models.BooleanField(default=False, verbose_name="Будущая ставка")

    def __str__(self):
        return f"{self.name_ru} ({self.rate}%)"

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

class CalculationHistory(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    amount = models.FloatField(verbose_name="Сумма")
    calculated_vat = models.FloatField(verbose_name="Рассчитанный НДС")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата расчёта")

    def __str__(self):
        return f"{self.country.name_ru} — {self.amount} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"

    class Meta:
        verbose_name = "История расчёта"
        verbose_name_plural = "История расчётов"