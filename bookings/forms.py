from datetime import datetime

from django import forms
from django.conf import settings
from django.utils import timezone

from bookings.models import Booking


class BookingForm(forms.ModelForm):
    recording_suffix = forms.CharField(
        label='Идентификатор записи',
        max_length=100,
        help_text='Последний элемент пути к записи',
        widget=forms.TextInput(attrs={
            'placeholder': 'meeting-2026-09-27-abc123',
            'class': 'flex-1 px-4 py-3 rounded-r-xl border border-gray-200 bg-gray-50 text-gray-900 '
                      'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 '
                      'focus:border-transparent transition-all duration-200'
        }),
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.recording_url:
            base = settings.RECORDING_URL_BASE
            if self.instance.recording_url.startswith(base):
                self.fields['recording_suffix'].initial = self.instance.recording_url[len(base):].strip('/')

    def clean_recording_suffix(self):
        suffix = self.cleaned_data['recording_suffix'].strip().strip('/')
        if not suffix:
            raise forms.ValidationError('Укажите идентификатор записи')
        return suffix

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        booking_time = cleaned_data.get('time')
        if booking_date and booking_time:
            booking_datetime = timezone.make_aware(datetime.combine(booking_date, booking_time))
            if booking_datetime <= timezone.now():
                self.add_error('date', 'Нельзя запланировать звонок на прошедшее время')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        suffix = self.cleaned_data['recording_suffix'].strip().strip('/')
        instance.recording_url = f'{settings.RECORDING_URL_BASE}{suffix}'
        if commit:
            instance.save()
        return instance
