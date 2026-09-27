from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
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
    }
    data.update(overrides)
    return data


def next_weekday(weekday):
    today = date.today()
    return today + timedelta(days=(weekday - today.weekday()) % 7)


def past_weekday():
    day = date.today() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


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
def test_recording_url_generated_on_create():
    booking = Booking(
        date=date.today() + timedelta(days=1),
        time=time(10, 0),
        client_name='Иван Иванов',
        topic='Обсуждение проекта',
    )
    booking.save()
    assert booking.recording_url.startswith(settings.RECORDING_URL_BASE)
    assert len(booking.recording_url) > len(settings.RECORDING_URL_BASE)


@pytest.mark.django_db
def test_recording_url_unchanged_on_update():
    booking = baker.make(Booking)
    original_url = booking.recording_url
    booking.topic = 'Новая тема'
    booking.save()
    assert booking.recording_url == original_url


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
def test_form_rejects_weekend():
    form = BookingForm(data=get_valid_form_data(date=next_weekday(5)))
    assert not form.is_valid()
    assert 'date' in form.errors


@pytest.mark.django_db
def test_form_rejects_off_grid_time():
    form = BookingForm(data=get_valid_form_data(time=time(10, 15)))
    assert not form.is_valid()
    assert 'time' in form.errors


@pytest.mark.django_db
def test_form_rejects_time_outside_working_hours():
    for booking_time in (time(7, 0), time(19, 30)):
        form = BookingForm(data=get_valid_form_data(time=booking_time))
        assert not form.is_valid()
        assert 'time' in form.errors


@pytest.mark.django_db
def test_form_rejects_occupied_slot():
    data = get_valid_form_data()
    baker.make(Booking, date=data['date'], time=data['time'])
    form = BookingForm(data=data)
    assert not form.is_valid()
    assert '__all__' in form.errors


@pytest.mark.django_db
def test_form_allows_editing_past_booking():
    booking = baker.make(
        Booking,
        date=past_weekday(),
        time=time(10, 0),
    )
    form = BookingForm(data=get_valid_form_data(
        date=booking.date,
        time=booking.time,
        topic='Новая тема',
    ), instance=booking)
    assert form.is_valid()


@pytest.mark.django_db
def test_form_accepts_future_datetime():
    form = BookingForm(data=get_valid_form_data())
    assert form.is_valid()
    booking = form.save()
    assert booking.pk is not None
    assert booking.recording_url.startswith(settings.RECORDING_URL_BASE)


@pytest.mark.django_db
def test_calendar_page_returns_200(client):
    response = client.get(reverse('bookings:calendar'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_booking_via_post(client):
    response = client.post(reverse('bookings:add'), data=get_valid_form_data())
    assert response.status_code == 302
    assert response.url == reverse('bookings:detail', kwargs={'pk': Booking.objects.get().pk})
    assert Booking.objects.count() == 1
    booking = Booking.objects.get()
    assert booking.client_name == 'Иван Иванов'
    assert booking.topic == 'Обсуждение проекта'
    assert booking.meeting_type == Booking.MeetingType.VIDEO
    assert booking.recording_url.startswith(settings.RECORDING_URL_BASE)


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
def test_create_booking_on_occupied_slot_fails(client):
    data = get_valid_form_data()
    baker.make(Booking, date=data['date'], time=data['time'])
    response = client.post(reverse('bookings:add'), data=data)
    assert response.status_code == 200
    assert '__all__' in response.context['form'].errors
    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_past_slots_unavailable_on_day_page(client):
    today = date.today()
    if today.weekday() >= 5:
        pytest.skip('Сегодня выходной')
    if timezone.now().time() <= time(9, 0):
        pytest.skip('Рабочий день ещё не начался')
    response = client.get(reverse('bookings:day', kwargs={
        'year': today.year, 'month': today.month, 'day': today.day,
    }))
    assert response.status_code == 200
    slots = {slot['time']: slot['is_available'] for slot in response.context['slots']}
    assert slots[time(9, 0)] is False


@pytest.mark.django_db
def test_upcoming_page_returns_200(client):
    response = client.get(reverse('bookings:upcoming'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_upcoming_page_lists_only_future_bookings(client):
    now = baker.make(
        Booking,
        date=date.today(),
        time=time(23, 59),
    )
    past = baker.make(
        Booking,
        date=date.today() - timedelta(days=1),
        time=time(10, 0),
    )
    response = client.get(reverse('bookings:upcoming'))
    bookings = list(response.context['bookings'])
    assert now in bookings
    assert past not in bookings


@pytest.mark.django_db
def test_delete_booking(client):
    booking = baker.make(Booking)
    url = reverse('bookings:delete', kwargs={'pk': booking.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == '/calendar/'
    assert not Booking.objects.filter(pk=booking.pk).exists()


@pytest.mark.django_db
def test_delete_confirmation_page_returns_200(client):
    booking = baker.make(Booking)
    response = client.get(reverse('bookings:delete', kwargs={'pk': booking.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_calendar_marks_today_by_moscow_date(client, monkeypatch):
    target_date = timezone.localdate() + timedelta(days=30)
    patched_now = datetime.combine(target_date, time(10, 0), tzinfo=ZoneInfo("UTC"))
    monkeypatch.setattr(timezone, 'now', lambda: patched_now)

    response = client.get(reverse('bookings:calendar'), {
        'year': target_date.year,
        'month': target_date.month,
    })
    assert response.status_code == 200
    days = {day['date']: day['is_today'] for day in response.context['days']}
    assert days[target_date] is True
    assert list(days.values()).count(True) == 1


@pytest.mark.django_db
def test_upcoming_page_uses_moscow_date_boundary(client, monkeypatch):
    patched_now = datetime(2026, 9, 27, 22, 0, tzinfo=ZoneInfo("UTC"))
    monkeypatch.setattr(timezone, 'now', lambda: patched_now)

    today_booking = baker.make(Booking, date=date(2026, 9, 28), time=time(10, 0))
    yesterday_booking = baker.make(Booking, date=date(2026, 9, 27), time=time(23, 0))

    response = client.get(reverse('bookings:upcoming'))
    bookings = list(response.context['bookings'])
    assert today_booking in bookings
    assert yesterday_booking not in bookings
