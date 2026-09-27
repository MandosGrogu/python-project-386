from django.urls import path

from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.DayView.as_view(), name='day'),
    path('calendar/booking/add/', views.BookingCreateView.as_view(), name='add'),
    path('calendar/booking/<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('calendar/booking/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='edit'),
    path('calendar/booking/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='delete'),
    path('upcoming/', views.UpcomingView.as_view(), name='upcoming'),
]
