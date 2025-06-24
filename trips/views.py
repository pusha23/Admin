from datetime import datetime

from django.contrib import messages
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

import openpyxl

from .forms import TripForm
from .models import Trip, Driver, Truck, Customer, Tariff
from .utils import get_tariff_price

# Убираем все декораторы, требующие авторизации
def redirect_by_role(request):
    user = request.user
    if user.groups.filter(name='Бухгалтер').exists():
        return redirect('trip_list')  # временно, заменим на свой маршрут
    elif user.groups.filter(name='Директор').exists():
        return redirect('trip_list')
    elif user.groups.filter(name='Логист').exists():
        return redirect('trip_list')
    return redirect('login')

@require_GET
def get_price_by_tariff(request):
    customer = request.GET.get('customer')
    direction = request.GET.get('direction')
    distance = request.GET.get('distance')
    points = request.GET.get('points')
    pallets = request.GET.get('pallets')
    tonnage = request.GET.get('tonnage')

    if not customer or not direction:
        return JsonResponse({"price": ""})

    distance = int(distance) if distance and distance.isdigit() else None
    points = int(points) if points and points.isdigit() else None
    pallets = int(pallets) if pallets and pallets.isdigit() else None
    try:
        tonnage = float(tonnage) if tonnage else None
    except ValueError:
        tonnage = None

    price = get_tariff_price(customer, direction, distance, points, pallets, tonnage)
    return JsonResponse({"price": price if price is not None else ""})

def trip_duplicate(request, pk):
    original = get_object_or_404(Trip, pk=pk)
    copy = Trip(
        date=original.date,
        customer=original.customer,
        driver=original.driver,
        truck=original.truck,
        direction=original.direction,
        route_sheet=original.route_sheet,
        tonnage=original.tonnage,
        distance=original.distance,
        weight=original.weight,
        pallets=original.pallets,
        points=original.points,
        price=original.price,
        comments=original.comments,
    )
    copy.save()
    messages.success(request, 'Рейс успешно продублирован')
    return redirect('trip_list')

@require_POST
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    trip.delete()
    messages.success(request, 'Рейс удалён')
    return redirect('trip_list')

def trip_list(request):
    trips = Trip.objects.select_related('driver', 'truck').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    query = request.GET.get('query')
    driver = request.GET.get('driver_name')

    if start_date:
        try:
            parsed_start = datetime.strptime(start_date, '%d.%m.%Y').date()
            trips = trips.filter(date__gte=parsed_start)
        except ValueError:
            pass
    if end_date:
        try:
            parsed_end = datetime.strptime(end_date, '%d.%m.%Y').date()
            trips = trips.filter(date__lte=parsed_end)
        except ValueError:
            pass

    if query:
        trips = trips.filter(
            models.Q(customer__name__icontains=query) |
            models.Q(direction__icontains=query) |
            models.Q(truck__number__icontains=query)
        )

    if driver:
        trips = trips.filter(driver__full_name=driver)

    trips = trips.order_by('-date')

    all_drivers = Driver.objects.values_list('full_name', flat=True).distinct().order_by('full_name')

    return render(request, 'trips/trip_list.html', {
        'trips': trips,
        'filter_start': start_date or '',
        'filter_end': end_date or '',
        'filter_query': query or '',
        'filter_driver': driver or '',
        'all_drivers': all_drivers
    })

def trip_create(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рейс успешно добавлен')
            return redirect('trip_list')
    else:
        form = TripForm()

    drivers = Driver.objects.all()
    trucks = Truck.objects.all()
    customers = Customer.objects.all()
    directions = Tariff.objects.values_list('direction', flat=True).distinct()

    return render(request, 'trips/trip_form.html', {
        'form': form,
        'drivers': drivers,
        'trucks': trucks,
        'customers': customers,
        'directions': directions,
    })

def trip_update(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            trip = form.save(commit=False)

            customer_name = form.cleaned_data['customer']
            driver_name = form.cleaned_data['driver_name']
            truck_number = form.cleaned_data['truck_number']

            trip.customer = get_object_or_404(Customer, name=customer_name)
            trip.driver = get_object_or_404(Driver, full_name=driver_name)
            trip.truck = get_object_or_404(Truck, number=truck_number)

            trip.save()
            messages.success(request, 'Рейс обновлён')
            return redirect('trip_list')
    else:
        form = TripForm(instance=trip)

    drivers = Driver.objects.all()
    trucks = Truck.objects.all()
    customers = Customer.objects.all()

    return render(request, 'trips/trip_form.html', {
        'form': form,
        'drivers': drivers,
        'trucks': trucks,
        'customers': customers
    })

def export_trips_xlsx(request):
    trips = Trip.objects.select_related('driver', 'truck').all()

    date = request.GET.get('date')
    direction = request.GET.get('direction')
    driver = request.GET.get('driver_name')

    if date:
        try:
            parsed_date = datetime.strptime(date, '%d.%m.%Y').date()
            trips = trips.filter(date=parsed_date)
        except ValueError:
            pass

    if direction:
        trips = trips.filter(direction__icontains=direction)
    if driver:
        trips = trips.filter(driver__full_name=driver)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Рейсы"

    ws.append([
        "Дата", "Заказчик", "Номер машины", "ФИО водителя",
        "Направление", "Маршрутный лист", "Тоннаж авто",
        "Километраж", "Вес", "Палеты", "Кол-во точек", "Стоимость", "Комментарий"
    ])

    for trip in trips:
        ws.append([
            trip.date.strftime('%d.%m.%Y'),
            trip.customer.name if trip.customer else '',
            trip.truck.number if trip.truck else '',
            trip.driver.full_name if trip.driver else '',
            trip.direction,
            trip.route_sheet,
            float(trip.tonnage) if trip.tonnage else '',
            trip.distance,
            float(trip.weight),
            trip.pallets,
            trip.points,
            float(trip.price),
            trip.comments,
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=reisy.xlsx'
    wb.save(response)
    return response
