from decimal import Decimal
import requests

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .models import Review
from .forms import ReviewForm

def _map_tmdb_genre_to_choice(genres):
    """
    TMDB genres(list[dict]) -> Review.genre (GENRE_CHOICES 중 하나)
    """
    if not genres:
        return "드라마"  # 기본값

    name = genres[0].get("name", "")

    # TMDB 한글 장르 → 네 choices에 맞추기
    if "액션" in name:
        return "액션"
    if "코미" in name:
        return "코미디"
    if "드라마" in name:
        return "드라마"
    if "로맨" in name or "멜로" in name:
        return "로맨스"
    if "스릴" in name:
        return "스릴러"
    if "공포" in name:
        return "공포"
    if "SF" in name or "과학" in name:
        return "SF"
    if "판타" in name:
        return "판타지"
    if "애니" in name:
        return "애니메이션"
    if "다큐" in name:
        return "다큐멘터리"

    # 매핑 안 되면 안전하게 드라마
    return "드라마"

def _tmdb_get(path: str, params=None):
    params = params or {}
    params.setdefault("language", "ko-KR")

    token = getattr(settings, "TMDB_READ_TOKEN", None)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    url = f"{settings.TMDB_BASE_URL}{path}"
    r = requests.get(url, params=params, headers=headers, timeout=10)

    if r.status_code >= 400:
        raise RuntimeError(f"TMDB {r.status_code} / token_set={bool(token)} / body={r.text}")

    return r.json()


@require_POST
def tmdb_sync_popular(request):
    """
    TMDB 인기 영화 20개를 가져와 Review 테이블에 저장 (중복은 tmdb_id로 방지)
    """
    popular = _tmdb_get("/movie/popular", params={"page": 1})

    for item in popular.get("results", []):
        movie_id = item.get("id")
        if not movie_id:
            continue

        detail = _tmdb_get(f"/movie/{movie_id}")
        credits = _tmdb_get(f"/movie/{movie_id}/credits")

        # 감독
        director = "Unknown"
        for c in credits.get("crew", []):
            if c.get("job") == "Director":
                director = c.get("name") or "Unknown"
                break

        # 배우 5명
        cast_names = [c.get("name") for c in credits.get("cast", [])[:5] if c.get("name")]
        actors = ", ".join(cast_names) if cast_names else "Unknown"

        # 개봉연도
        release_date = detail.get("release_date")
        release_year = int(release_date[:4]) if release_date else 0

        Review.objects.update_or_create(
            tmdb_id=movie_id,
            defaults={
                "is_from_tmdb": True,
                "title": detail.get("title", "") or "",
                "release_year": release_year,
                "genre": _map_tmdb_genre_to_choice(detail.get("genres")),
                "rating": Decimal("3.0"),
                "director": director,
                "actors": actors,
                "runtime": detail.get("runtime") or 0,
                "content": detail.get("overview") or "",
            }
        )

    return redirect("reviews:list")


def review_list(request):
    sort = request.GET.get("sort", "latest")

    sort_map = {
        "title_asc": "title",
        "title_desc": "-title",
        "year_asc": "release_year",
        "year_desc": "-release_year",
        "rating_asc": "rating",
        "rating_desc": "-rating",
    }

    order = sort_map.get(sort, "-id")
    reviews = Review.objects.all().order_by(order)

    return render(request, "reviews/list.html", {"reviews": reviews, "sort": sort})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/detail.html", {"review": review})

def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("reviews:list")
    else:
        form = ReviewForm()
    return render(request, "reviews/form.html", {"form": form, "mode": "create"})

def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("reviews:detail", pk=review.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, "reviews/form.html", {"form": form, "mode": "update"})


def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
    return redirect("reviews:list")
