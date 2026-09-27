from django.urls import path

from bookings import views

app_name = 'bookings'

urlpatterns = [
    path('', views.CalendarView.as_view(), name='calendar'),
    path('<int:year>/<int:month>/<int:day>/', views.DayView.as_view(), name='day'),
    path('booking/add/', views.BookingCreateView.as_view(), name='add'),
    path('booking/<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('booking/<int:pk>/edit/', views.BookingUpdateView.as_view(), name='edit'),
    path('booking/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='delete'),
]
