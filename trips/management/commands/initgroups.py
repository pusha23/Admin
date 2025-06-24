from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from trips.models import Trip  # замени на актуальную модель, если нужно

class Command(BaseCommand):
    help = 'Создаёт группы пользователей: Логист, Бухгалтер и Директор'

    def handle(self, *args, **kwargs):
        groups_permissions = {
            'Логист': ['add_trip', 'change_trip', 'view_trip'],
            'Бухгалтер': ['view_trip'],
            'Директор': ['view_trip'],
        }

        trip_ct = ContentType.objects.get_for_model(Trip)

        for group_name, perms in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            for codename in perms:
                permission = Permission.objects.get(codename=codename, content_type=trip_ct)
                group.permissions.add(permission)
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" обновлена'))

        self.stdout.write(self.style.SUCCESS('Группы и права успешно назначены.'))
