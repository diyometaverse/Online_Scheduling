from django.urls import path
from .views import admin_delete_booking

from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('update/<int:pk>/', views.update_booking, name='update_booking'),
    path('delete/<int:pk>/', views.delete_booking, name='delete_booking'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('details/<int:pk>/', views.booking_details, name='booking_details'),

    # Admin
    path('admin-update/<int:pk>/', views.admin_update_booking, name='admin_update_booking'),
    path('approve/<int:pk>/', views.approve_booking, name='approve_booking'),
    path('disapprove/<int:pk>/', views.disapprove_booking, name='disapprove_booking'),
    path('reschedule/<int:pk>/', views.reschedule_booking, name='reschedule_booking'),
    path('admin-dashboard/delete/<int:booking_id>/', admin_delete_booking, name='admin_delete_booking'),

]
