from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from trips.views import redirect_by_role

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('', views.trip_list, name='trip_list'),
    path('create/', views.trip_create, name='trip_create'),
    path('export/', views.export_trips_xlsx, name='export_trips'),
    path('<int:pk>/edit/', views.trip_update, name='trip_update'),
    path('get-price/', views.get_price_by_tariff, name='get_price_by_tariff'),
    path('trips/<int:pk>/duplicate/', views.trip_duplicate, name='trip_duplicate'),
    path('trips/<int:pk>/delete/', views.trip_delete, name='trip_delete'),

    # АВТОРИЗАЦИЯ
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redirect-by-role/', redirect_by_role, name='redirect_by_role'),
]
