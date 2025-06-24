from django.db import models
from django.core.validators import MinValueValidator


class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название заказчика")

    class Meta:
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"

    def __str__(self):
        return self.name



class Driver(models.Model):
    full_name = models.CharField("ФИО водителя", max_length=255)

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

    def __str__(self):
        return self.full_name

class Truck(models.Model):
    number = models.CharField("Номер машины", max_length=50)

    class Meta:
        verbose_name = "Машина"
        verbose_name_plural = "Машины"

    def __str__(self):
        return self.number

class Tariff(models.Model):
    customer = models.CharField("Заказчик", max_length=255)
    direction = models.CharField("Направление", max_length=255, default="любой")
    base_price = models.IntegerField("Базовая ставка", default=0)
    price_per_km = models.FloatField("Цена за км", null=True, blank=True)
    price_per_point = models.FloatField("Цена за точку", null=True, blank=True)
    pallet_based_prices = models.JSONField("Цены по количеству палет", null=True, blank=True)
    tonnage_based_prices = models.JSONField("Цены по тоннажу машины", null=True, blank=True)
    extra_point_price_per_tonnage = models.JSONField("Цена за доп. точку по тоннажу", null=True, blank=True)
    max_points_per_tonnage = models.JSONField("Максимум точек по тоннажу (для расчёта доплаты)", null=True, blank=True)
    



    class Meta:
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self):
        return f"{self.customer} — {self.direction} — {self.base_price}₽"

class Trip(models.Model):
    date = models.DateField(verbose_name="Дата рейса")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, verbose_name="Заказчик")
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, verbose_name="Водитель")
    truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, verbose_name="Машина")
    direction = models.CharField(max_length=255, verbose_name="Направление")

    # Сделаны необязательными:
    route_sheet = models.TextField(blank=True, null=True, verbose_name="Маршрутный лист")
    tonnage = models.PositiveIntegerField(blank=True, null=True, verbose_name="Тоннаж авто")
    distance = models.PositiveIntegerField(blank=True, null=True, verbose_name="Километраж")
    pallets = models.PositiveIntegerField(blank=True, null=True, verbose_name="Палеты")
    points = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество точек")

    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Вес")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость рейса")
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True, verbose_name="Комментарии")

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"

    def __str__(self):
        return f"{self.date} — {self.driver_name} — {self.direction}"

