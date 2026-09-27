from datetime import date, time, timedelta

import pytest
from django.urls import reverse
from model_bakery import baker

from bookings.forms import BookingForm
from bookings.models import Booking


def get_valid_form_data(**overrides):
    data = {
        'date': date.today() + timedelta(days=1),
        'time': time(10, 0),
        'client_name': 'Иван Иванов',
        'topic': 'Обсуждение проекта',
        'meeting_type': Booking.MeetingType.VIDEO,
        'recording_suffix': 'meeting-2026-09-28-abc123',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_booking_str():
    booking = baker.make(Booking, client_name='Иван Иванов')
    assert str(booking) == f'{booking.client_name} — {booking.date} {booking.time}'


@pytest.mark.django_db
def test_booking_fields():
    booking = baker.make(
        Booking,
        client_name='Иван Иванов',
        topic='Обсуждение проекта',
        meeting_type=Booking.MeetingType.AUDIO,
        recording_url='https://recordings.example.com/meeting-1',
    )
    assert booking.client_name == 'Иван Иванов'
    assert booking.topic == 'Обсуждение проекта'
    assert isinstance(booking.date, date)
    assert isinstance(booking.time, time)
    assert booking.meeting_type == Booking.MeetingType.AUDIO
    assert booking.recording_url.startswith('http')
    assert booking.created_at is not None
    assert booking.updated_at is not None


@pytest.mark.django_db
def test_form_rejects_past_datetime():
    form = BookingForm(data=get_valid_form_data(
        date=date.today() - timedelta(days=1),
        time=time(10, 0),
    ))
    assert not form.is_valid()
    assert 'date' in form.errors


@pytest.mark.django_db
def test_form_rejects_past_time_today():
    form = BookingForm(data=get_valid_form_data(
        date=date.today(),
        time=time(0, 0),
    ))
    assert not form.is_valid()
    assert 'date' in form.errors


@pytest.mark.django_db
def test_form_accepts_future_datetime():
    form = BookingForm(data=get_valid_form_data())
    assert form.is_valid()
    booking = form.save()
    assert booking.pk is not None
    assert booking.recording_url == 'https://recordings.example.com/meeting-2026-09-28-abc123'


@pytest.mark.django_db
def test_calendar_page_returns_200(client):
    response = client.get(reverse('bookings:calendar'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_booking_via_post(client):
    response = client.post(reverse('bookings:add'), data=get_valid_form_data())
    assert response.status_code == 302
    assert response.url == '/'
    assert Booking.objects.count() == 1
    booking = Booking.objects.get()
    assert booking.client_name == 'Иван Иванов'
    assert booking.topic == 'Обсуждение проекта'
    assert booking.meeting_type == Booking.MeetingType.VIDEO
    assert booking.recording_url == 'https://recordings.example.com/meeting-2026-09-28-abc123'


@pytest.mark.django_db
def test_create_booking_with_empty_client_name_fails(client):
    response = client.post(reverse('bookings:add'), data=get_valid_form_data(client_name=''))
    assert response.status_code == 200
    assert 'client_name' in response.context['form'].errors
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_create_booking_in_past_fails(client):
    response = client.post(reverse('bookings:add'), data=get_valid_form_data(
        date=date.today() - timedelta(days=1),
    ))
    assert response.status_code == 200
    assert 'date' in response.context['form'].errors
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_delete_booking(client):
    booking = baker.make(Booking)
    url = reverse('bookings:delete', kwargs={'pk': booking.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == '/'
    assert not Booking.objects.filter(pk=booking.pk).exists()


@pytest.mark.django_db
def test_delete_confirmation_page_returns_200(client):
    booking = baker.make(Booking)
    response = client.get(reverse('bookings:delete', kwargs={'pk': booking.pk}))
    assert response.status_code == 200
