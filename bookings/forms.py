from datetime import datetime, time

from django import forms
from django.conf import settings
from django.utils import timezone

from bookings.models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'client_name', 'topic', 'meeting_type']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 '
                          'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                          'focus:border-transparent transition-all duration-200'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'step': 1800,
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 '
                          'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                          'focus:border-transparent transition-all duration-200'
            }),
            'client_name': forms.TextInput(attrs={
                'placeholder': 'Иван Иванов',
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 '
                          'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 '
                          'focus:border-transparent transition-all duration-200'
            }),
            'topic': forms.TextInput(attrs={
                'placeholder': 'Обсуждение проекта',
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 '
                          'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 '
                          'focus:border-transparent transition-all duration-200'
            }),
            'meeting_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 '
                          'focus:outline-none focus:ring-2 focus:ring-blue-500 '
                          'focus:border-transparent transition-all duration-200'
            }),
        }

    def clean_date(self):
        booking_date = self.cleaned_data['date']
        if booking_date.weekday() >= 5:
            raise forms.ValidationError('В выходные бронирование недоступно')
        return booking_date

    def clean_time(self):
        booking_time = self.cleaned_data['time']
        if booking_time.minute not in (0, 30):
            raise forms.ValidationError('Время должно быть кратно 30 минутам')
        start = time(settings.WORKING_HOURS_START, 0)
        end = time(settings.WORKING_HOURS_END, 0)
        if not start <= booking_time < end:
            raise forms.ValidationError(
                f'Время должно быть в рабочие часы '
                f'({settings.WORKING_HOURS_START}:00–{settings.WORKING_HOURS_END}:00)'
            )
        return booking_time

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        booking_time = cleaned_data.get('time')
        if booking_date and booking_time:
            if self.instance.pk is None:
                booking_datetime = timezone.make_aware(datetime.combine(booking_date, booking_time))
                if booking_datetime <= timezone.now():
                    self.add_error('date', 'Нельзя запланировать звонок на прошедшее время')
            occupied = Booking.objects.filter(date=booking_date, time=booking_time)
            if self.instance.pk is not None:
                occupied = occupied.exclude(pk=self.instance.pk)
            if occupied.exists():
                self.add_error(None, 'Слот уже занят')
        return cleaned_data
