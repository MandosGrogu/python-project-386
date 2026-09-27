from datetime import date, datetime, time, timedelta

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.base import TemplateView

from bookings.forms import BookingForm
from bookings.models import Booking


class CalendarView(TemplateView):
    template_name = 'bookings/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        year = self.request.GET.get('year', today.year)
        month = self.request.GET.get('month', today.month)
        try:
            year = int(year)
            month = int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year, 12, 31)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        days_in_month = []
        for day in range(1, last_day.day + 1):
            current_date = date(year, month, day)
            bookings = Booking.objects.filter(date=current_date).order_by('time')
            days_in_month.append({
                'date': current_date,
                'bookings': bookings,
                'is_today': current_date == today,
            })

        if month == 1:
            prev_month = date(year - 1, 12, 1)
            next_month = date(year, 2, 1)
        elif month == 12:
            prev_month = date(year, 11, 1)
            next_month = date(year + 1, 1, 1)
        else:
            prev_month = date(year, month - 1, 1)
            next_month = date(year, month + 1, 1)

        context.update({
            'days': days_in_month,
            'current_month': first_day,
            'prev_month': prev_month,
            'next_month': next_month,
            'slot_duration': settings.SLOT_DURATION_MINUTES,
            'working_hours_start': settings.WORKING_HOURS_START,
            'working_hours_end': settings.WORKING_HOURS_END,
        })
        return context


class DayView(TemplateView):
    template_name = 'bookings/day.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_date = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        now = timezone.now()

        booked_times = set(
            Booking.objects.filter(date=selected_date).values_list('time', flat=True)
        )

        slots = []
        current_time = time(settings.WORKING_HOURS_START, 0)
        end_time = time(settings.WORKING_HOURS_END, 0)

        while current_time < end_time:
            slot_datetime = timezone.make_aware(datetime.combine(selected_date, current_time))
            slots.append({
                'time': current_time,
                'is_available': current_time not in booked_times and slot_datetime > now,
            })
            dt = datetime.combine(selected_date, current_time) + timedelta(minutes=settings.SLOT_DURATION_MINUTES)
            current_time = dt.time()

        context.update({
            'date': selected_date,
            'slots': slots,
        })
        return context


class BookingCreateView(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def get_initial(self):
        initial = super().get_initial()
        date_str = self.request.GET.get('date')
        time_str = self.request.GET.get('time')
        if date_str:
            initial['date'] = date_str
        if time_str:
            initial['time'] = time_str
        return initial

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Слот уже занят')
            return self.form_invalid(form)
        messages.success(self.request, 'Бронирование создано')
        return response

    def get_success_url(self):
        return reverse('bookings:detail', kwargs={'pk': self.object.pk})


class BookingUpdateView(UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'Слот уже занят')
            return self.form_invalid(form)
        messages.success(self.request, 'Бронирование обновлено')
        return response

    def get_success_url(self):
        return reverse('bookings:detail', kwargs={'pk': self.object.pk})


class BookingDeleteView(DeleteView):
    model = Booking

    def get_success_url(self):
        messages.success(self.request, 'Бронирование удалено')
        return '/calendar/'


class BookingDetailView(DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'


class UpcomingView(TemplateView):
    template_name = 'bookings/upcoming.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.localtime(timezone.now())
        context['bookings'] = Booking.objects.filter(
            Q(date__gt=now.date()) | Q(date=now.date(), time__gte=now.time())
        ).order_by('date', 'time')
        return context
