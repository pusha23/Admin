from django.contrib.auth.decorators import user_passes_test
from .models import Tariff

def group_required(*group_names):
    """
    Декоратор, проверяющий, принадлежит ли пользователь к указанным группам.
    Пример использования: @group_required('Логист', 'Директор')
    """
    def in_groups(user):
        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name__in=group_names).exists():
                return True
        return False
    return user_passes_test(in_groups)


def get_tariff_price(customer, direction=None, distance=None, points=None, pallets=None, tonnage=None):
    try:
        tariffs = Tariff.objects.filter(customer__iexact=customer)

        for tariff in tariffs:
            if tariff.direction.lower() != 'любой' and tariff.direction.lower() != (direction or '').lower():
                continue

            if tariff.pallet_based_prices and pallets is not None:
                pallets_str = str(int(pallets))
                price = tariff.pallet_based_prices.get(pallets_str)
                if price is not None:
                    return float(price)

            if tariff.tonnage_based_prices and tonnage is not None:
                tonnage_clean = str(float(tonnage)).rstrip('0').rstrip('.')
                price = tariff.tonnage_based_prices.get(tonnage_clean)
                if price is not None:
                    price = float(price)
                    limit_map = tariff.max_points_per_tonnage or {}
                    extra_map = tariff.extra_point_price_per_tonnage or {}

                    limit = int(limit_map.get(tonnage_clean, 0))
                    extra_price = float(extra_map.get(tonnage_clean, 0))

                    if points is not None and points > limit:
                        extra_points = points - limit
                        price += extra_points * extra_price

                    return round(price, 2)

            base = float(tariff.base_price or 0)
            km_price = float(tariff.price_per_km or 0) * (distance or 0)
            point_price = 0

            if tonnage and points:
                tonnage_clean = str(float(tonnage)).rstrip('0').rstrip('.')
                limit_map = tariff.max_points_per_tonnage or {}
                extra_map = tariff.extra_point_price_per_tonnage or {}

                max_points = int(limit_map.get(tonnage_clean, 0))
                extra_price = float(extra_map.get(tonnage_clean, 0))

                if points > max_points:
                    point_price = extra_price * (points - max_points)
            else:
                point_price = float(tariff.price_per_point or 0) * (points or 0)

            return round(base + km_price + point_price, 2)

        return None

    except Exception as e:
        print(f"[ERROR] Ошибка при расчёте тарифа: {e}")
        return None
