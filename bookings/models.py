from django.db import models
from django.urls import reverse


class Booking(models.Model):
    class MeetingType(models.TextChoices):
        VIDEO = 'video', 'Видеозвонок'
        AUDIO = 'audio', 'Аудиозвонок'
        PERSONAL = 'personal', 'Личная встреча'

    date = models.DateField('Дата')
    time = models.TimeField('Время')
    client_name = models.CharField('Имя клиента', max_length=200)
    topic = models.CharField('Тема', max_length=300)
    meeting_type = models.CharField(
        'Тип встречи',
        max_length=20,
        choices=MeetingType.choices,
        default=MeetingType.VIDEO,
    )
    recording_url = models.URLField('Ссылка на запись', blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'time'],
                name='unique_slot',
            ),
        ]

    def __str__(self):
        return f'{self.client_name} — {self.date} {self.time}'

    def get_absolute_url(self):
        return reverse('bookings:detail', kwargs={'pk': self.pk})
