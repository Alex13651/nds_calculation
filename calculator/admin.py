from django.contrib import admin
from .models import Country, CalculationHistory

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name_ru', 'name_en', 'rate', 'future')
    search_fields = ('name_ru', 'name_en')
    list_filter = ('future',)
    ordering = ('name_ru',)

@admin.register(CalculationHistory)
class CalculationHistoryAdmin(admin.ModelAdmin):
    list_display = ('country', 'amount', 'calculated_vat', 'created_at')
    list_filter = ('country', 'created_at')
    readonly_fields = ('created_at',)