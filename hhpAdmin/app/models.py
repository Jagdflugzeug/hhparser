from django.db import models
from django.core.validators import MinValueValidator
from datetime import timedelta


class Hub(models.Model):
    name = models.CharField(max_length=512)
    active = models.BooleanField(default=False)
    check_period = models.DurationField(validators=[MinValueValidator(timedelta(minutes=1))],
                                        help_text="Минимальный период опроса должнен быть больше 1 минуты.")
    url = models.CharField(max_length=256, unique=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_period__gte=timedelta(minutes=1)),
                name='check_period_gte_1_minute'
            ),
        ]

    def to_dict(self):
        return {
            "name": self.name,
            "active": self.active,
            "check_period": self.check_period.total_seconds()
        }

    def __str__(self):
        return f'[{self.pk}] {self.name}'


class HubArticle(models.Model):
    title = models.TextField()
    hub = models.ForeignKey('Hub', on_delete=models.SET_NULL, null=True)
    post_link = models.CharField(max_length=256, unique=True)
    author_name = models.CharField(max_length=128)
    author_link = models.CharField(max_length=128)
    datetime_published = models.DateField()

    def to_dict(self):
        return {
            "title": self.title,
            "post_link": self.post_link,
            "author_name": self.author_name,
            "author_link": self.author_link,
            "time_published": self.datetime_published.timestamp() if self.datetime_published else None
        }

    def __str__(self):
        return f'[{self.pk}] {self.title}'