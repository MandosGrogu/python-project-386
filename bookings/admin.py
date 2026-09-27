from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'client_name', 'topic', 'meeting_type']
    list_filter = ['date', 'meeting_type']
    search_fields = ['client_name', 'topic']
