import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from .models import Review
from .forms import ReviewForm

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
        # 토큰이 실제로 세팅됐는지까지 같이 보여주기(토큰 값은 노출 X)
        raise RuntimeError(f"TMDB {r.status_code} / token_set={bool(token)} / body={r.text}")

    return r.json()

def _get_genre_map_ko() -> dict[int, str]:
    # { 28: "액션", 35: "코미디", ... }
    data = _tmdb_get("/genre/movie/list", params={"language": "ko-KR"})
    return {g["id"]: g["name"] for g in data.get("genres", [])}

def sort_tmdb_movies(movies, sort):
    if sort == "title_asc":
        return sorted(movies, key=lambda x: x["title"] or "")
    if sort == "title_desc":
        return sorted(movies, key=lambda x: x["title"] or "", reverse=True)

    if sort == "year_asc":
        return sorted(movies, key=lambda x: x["release_year"] or 0)
    if sort == "year_desc":
        return sorted(movies, key=lambda x: x["release_year"] or 0, reverse=True)

    if sort == "rating_asc":
        return sorted(movies, key=lambda x: x["rating"] or 0)
    if sort == "rating_desc":
        return sorted(movies, key=lambda x: x["rating"] or 0, reverse=True)

    # latest / oldest 등은 TMDB 기본 순서 유지
    return movies

def review_list(request):
    sort = request.GET.get("sort", "latest")
    sort_map = {
        "latest": "-id",
        "oldest": "id",
        "title_asc": "title",
        "title_desc": "-title",
        "year_asc": "release_year",
        "year_desc": "-release_year",
        "rating_asc": "rating",
        "rating_desc": "-rating",
    }
    order = sort_map.get(sort, "-id")
    reviews = Review.objects.all().order_by(order)

    pages = int(request.GET.get("pages", 1))

    tmdb_movies = []
    tmdb_error = None

    try:
        genre_map = _get_genre_map_ko()

        for page in range(1, pages + 1):
            popular = _tmdb_get("/movie/popular", params={"page": page, "language": "ko-KR"})

            for item in popular.get("results", []):
                release_date = item.get("release_date") or ""
                release_year = int(release_date.split("-")[0]) if release_date else None

                genre_ids = item.get("genre_ids") or []
                # 첫 장르만 표시 (원하면 여러 개 join 가능)
                genre_ko = genre_map.get(genre_ids[0], "기타") if genre_ids else "기타"

                vote_avg = float(item.get("vote_average") or 0.0)  # 0~10
                rating_5 = round((vote_avg / 2) * 2) / 2           # 0.5 step, 0~5

                poster_path = item.get("poster_path")
                poster_url = (
                    f"{settings.TMDB_IMG_BASE}/w200{poster_path}"
                    if poster_path else ""
                )

                tmdb_movies.append({
                    "tmdb_id": item.get("id"),
                    "title": item.get("title") or "",
                    "release_year": release_year,
                    "genre": genre_ko,
                    "rating": rating_5,
                    "poster_url": poster_url,
                })

        tmdb_movies = tmdb_movies[: pages * 20]

        tmdb_movies = sort_tmdb_movies(tmdb_movies, sort)

    except Exception as e:
        tmdb_error = str(e)

    return render(request, "reviews/list.html", {
        "reviews": reviews,
        "sort": sort,
        "tmdb_movies": tmdb_movies,
        "tmdb_pages": pages,
        "tmdb_error": tmdb_error,
    })

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/detail.html", {"review": review})

def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            if form.is_valid():
                form.save()
                return redirect("reviews:list")
    else:
        form = ReviewForm()
    return render(request, "reviews/form.html", {"form": form, "mode": "create"})

def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance = review)
        if form.is_valid():
            form.save()
            return render(request, "reviews/detail.html", {"review": review})
    else:
        form = ReviewForm(instance = review)
    return render(request, "reviews/form.html", {"form": form, "mode": "create"})

def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        review.delete()
    return redirect("reviews:list")

