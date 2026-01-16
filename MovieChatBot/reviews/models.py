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

GENRE_CHOICES = [
    ("액션", "액션"),
    ("코미디", "코미디"),
    ("드라마", "드라마"),
    ("로맨스", "로맨스"),
    ("스릴러", "스릴러"),
    ("공포", "공포"),
    ("SF", "SF"),
    ("판타지", "판타지"),
    ("애니메이션", "애니메이션"),
    ("다큐멘터리", "다큐멘터리"),
]

class Review(models.Model):
    tmdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    is_from_tmdb = models.BooleanField(default=False)

    title = models.CharField(max_length=100)
    release_year = models.IntegerField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
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
    runtime = models.IntegerField()  # 총 분

    @property
    def runtime_hm(self):
        h = self.runtime // 60
        m = self.runtime % 60
        return f"{h}시간 {m}분" if h else f"{m}분"