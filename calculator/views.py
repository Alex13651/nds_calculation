from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from collections import Counter
from .models import Country, CalculationHistory
from .vat_data import find as find_in_file, parse_amount, calc, fmt_rate_full

def index(request):
    query = request.GET.get('country', '').strip()
    amount_raw = request.GET.get('amount', '').strip()
    result = None
    error = None
    ambiguous = None

    if query:
        amount = parse_amount(amount_raw) if amount_raw else None
        found_countries = Country.objects.filter(
            Q(name_ru__icontains=query) | Q(name_en__icontains=query)
        )
        if not found_countries.exists():
            found_names, exact = find_in_file(query)
            if found_names:
                found_countries = Country.objects.filter(name_ru=found_names[0])

        if not found_countries.exists():
            error = "Страна не найдена."
        elif found_countries.count() == 1:
            c = found_countries.first()
            result = {
                "ru": c.name_ru, "en": c.name_en, "rate": c.rate,
                "rate_str": fmt_rate_full({"rate": c.rate, "future": c.future}) if c.rate is not None else None,
                "note": c.note, "scope": c.scope,
                "future": c.future, "amount": None,
            }
            if amount is not None and c.rate is not None:
                result["amount"] = calc(c.name_ru, amount)
                CalculationHistory.objects.create(
                    country=c, amount=amount, calculated_vat=amount * (c.rate / 100)
                )
        else:
            ambiguous = [c.name_ru for c in found_countries[:5]]

    all_countries_db = Country.objects.all().order_by('name_ru')
    all_countries = [
        {"ru": c.name_ru, "rate_str": f"{c.rate:g}%" if c.rate is not None else "нет"}
        for c in all_countries_db
    ]

    return render(request, 'index.html', {
        "query": query, "amount_raw": amount_raw,
        "result": result, "error": error, "ambiguous": ambiguous,
        "all_countries": all_countries
    })

def api_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    countries = Country.objects.filter(Q(name_ru__icontains=query) | Q(name_en__icontains=query))[:8]
    results = [{"ru": c.name_ru, "en": c.name_en, "rate_str": f"{c.rate:g}%" if c.rate is not None else "нет"} for c in countries]
    return JsonResponse(results, safe=False)

def api_compare(request):
    amount = parse_amount(request.GET.get('amount', '1000')) or 1000
    names = request.GET.get('countries', '').strip()
    if names:
        selected_names = [n.strip() for n in names.split(",") if n.strip()]
        countries = Country.objects.filter(name_ru__in=selected_names)
    else:
        default_names = ["Германия", "Франция", "Италия", "Испания", "Великобритания", "Швеция", "Дания", "Венгрия", "Россия", "США", "ОАЭ", "Китай"]
        countries = Country.objects.filter(name_ru__in=default_names)

    data = []
    for c in countries:
        if c.rate is None: continue
        k = c.rate / 100
        data.append({"country": c.name_ru, "rate": c.rate, "net": amount, "vat": round(amount * k, 2), "gross": round(amount * (1 + k), 2)})
    data.sort(key=lambda x: x["gross"])
    return JsonResponse({"amount": amount, "items": data})

def api_distribution(request):
    rates = list(Country.objects.exclude(rate__isnull=True).values_list('rate', flat=True))
    counter = Counter(rates)
    items = sorted(counter.items())
    return JsonResponse({"labels": [f"{r:g}%" for r, _ in items], "values": [n for _, n in items]})

def api_map_data(request):
    rows = [{"iso": c.iso_code, "country": c.name_ru, "rate": c.rate} for c in Country.objects.exclude(rate__isnull=True).exclude(iso_code='')]
    return JsonResponse(rows, safe=False)