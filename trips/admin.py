from django.contrib import admin
from .models import Trip, Tariff, Driver, Truck, Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name"]

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("customer", "direction", "price_per_km", "price_per_point", "base_price")
    list_filter = ("customer", "direction")
    fieldsets = (
        (None, {
            'fields': (
                'customer', 'direction', 'base_price', 
                'price_per_km', 'price_per_point',
                'pallet_based_prices', 'tonnage_based_prices',
                'extra_point_price_per_tonnage', 'max_points_per_tonnage',
            )
        }),
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("full_name",)
    search_fields = ("full_name",)

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ("number",)
    search_fields = ("number",)

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('date', 'customer', 'driver', 'direction', 'price')
    list_filter = ('customer', 'driver', 'date')
    search_fields = ('driver__full_name', 'truck__number', 'direction')
    ordering = ('-date',)

