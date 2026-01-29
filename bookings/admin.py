from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'session_datetime', 'status')
    list_filter = ('status', 'service_type')
    search_fields = ('user__username',)

    actions = ['approve_bookings', 'disapprove_bookings']

    def approve_bookings(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} bookings approved successfully.")
    approve_bookings.short_description = "Approve selected bookings"

    def disapprove_bookings(self, request, queryset):
        updated = queryset.update(status='disapproved')
        self.message_user(request, f"{updated} bookings disapproved.")
    disapprove_bookings.short_description = "Disapprove selected bookings"

admin.site.register(Booking, BookingAdmin)
