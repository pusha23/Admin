from django import forms
from .models import Trip, Driver, Truck, Customer  # Добавили Customer
from datetime import date


class TripForm(forms.ModelForm):
    date = forms.DateField(
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        label='Дата',
        initial=date.today,
        widget=forms.DateInput(format='%d.%m.%Y', attrs={
            'class': 'form-control',
            'placeholder': 'дд.мм.гггг'
        })
    )

    comments = forms.CharField(
        label='Комментарии',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите комментарии',
            'rows': 3
        }),
        required=False
    )

    route_sheet = forms.CharField(
        label='Маршрутный лист',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Маршрутный лист'
        }),
        required=False
    )

    driver_name = forms.CharField(
        label='Водитель',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'drivers-list',
            'placeholder': 'Введите ФИО'
        })
    )

    truck_number = forms.CharField(
        label='Машина',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'trucks-list',
            'placeholder': 'Введите номер машины',
        })
    )

    customer = forms.CharField(
        label='Заказчик',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'customers-list',
            'placeholder': 'Введите заказчика'
        })
    )

    class Meta:
        model = Trip
        exclude = ['driver', 'truck', 'customer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if instance:
            self.fields['driver_name'].initial = instance.driver.full_name if instance.driver else ''
            self.fields['truck_number'].initial = instance.truck.number if instance.truck else ''
            self.fields['customer'].initial = instance.customer.name if hasattr(instance.customer, 'name') else instance.customer

        # Добавляем атрибуты для автодополнения
        self.fields['direction'].widget.attrs.update({
            'class': 'form-control',
            'list': 'directions-list',
            'placeholder': 'Введите направление'
        })

        self.order_fields([
            'comments',
            'date',
            'customer',
            'driver_name',
            'truck_number',
            'direction',
            'route_sheet',
            'tonnage',
            'distance',
            'weight',
            'pallets',
            'points',
            'price'
        ])

        for name, field in self.fields.items():
            if name not in ['date', 'route_sheet', 'driver_name', 'truck_number', 'customer', 'direction']:
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs.setdefault('placeholder', field.label)
            
    def save(self, commit=True):
        instance = super().save(commit=False)

        driver_name = self.cleaned_data.get('driver_name')
        if driver_name:
            driver_obj, _ = Driver.objects.get_or_create(full_name=driver_name)
            instance.driver = driver_obj

        truck_number = self.cleaned_data.get('truck_number')
        if truck_number:
            truck_obj, _ = Truck.objects.get_or_create(number=truck_number)
            instance.truck = truck_obj

        customer_name = self.cleaned_data.get('customer')
        if customer_name:
            customer_obj, _ = Customer.objects.get_or_create(name=customer_name)
            instance.customer = customer_obj

        # Сохраняем комментарий
        instance.comments = self.cleaned_data.get('comments')

        if commit:
            instance.save()

        return instance
