from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

RATING_CHOICES = [
    (Decimal("1.0"), "1.0"),
    (Decimal("1.5"), "1.5"),
    (Decimal("2.0"), "2.0"),
    (Decimal("2.5"), "2.5"),
    (Decimal("3.0"), "3.0"),
    (Decimal("3.5"), "3.5"),
    (Decimal("4.0"), "4.0"),
    (Decimal("4.5"), "4.5"),
    (Decimal("5.0"), "5.0"),
]

class Review(models.Model):
    title = models.CharField(max_length=100)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=50)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=RATING_CHOICES,
        validators=[MinValueValidator(Decimal("1.0")), MaxValueValidator(Decimal("5.0"))],
    )

    director = models.CharField(max_length=100)
    actors = models.CharField(max_length=200)
    runtime = models.IntegerField()
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title