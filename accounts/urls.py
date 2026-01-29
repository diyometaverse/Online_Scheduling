from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('book-now/', views.book_now, name='book_now'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),

    # Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # FIX: Move delete user OUT of "admin/"
    path('manage/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]
