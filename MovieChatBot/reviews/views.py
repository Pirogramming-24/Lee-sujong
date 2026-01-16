from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.http import JsonResponse
from reviews.rag.retriever import retrieve_movies
from reviews.rag.prompt import build_prompt
from openai import OpenAI
from .models import Review
from .forms import ReviewForm
import requests
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def chat_page(request):
    return render(request, "reviews/chat.html")

def movie_chatbot(request):
    q = request.GET.get("q")
    if not q:
        return JsonResponse({"error": "query required"}, status=400)

    contexts = retrieve_movies(q)
    prompt = build_prompt(q, contexts)

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "너는 영화 추천 전문가다."},
            {"role": "user", "content": prompt},
        ],
    )

    return JsonResponse({
        "answer": res.choices[0].message.content,
        "contexts": contexts,
    })

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

        # 이미지 경로 설정
        poster_path = detail.get("poster_path")
        tmdb_poster_url = (
            f"{settings.TMDB_IMG_BASE}/w500{poster_path}"
            if poster_path else ""
        )

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
                "tmdb_poster_url": tmdb_poster_url,
                "user_poster_image": None,
            }
        )

    return redirect("reviews:list")


def review_list(request):
    sort = request.GET.get("sort", "latest")
    source = request.GET.get("source")
    search_txt = request.GET.get('search_txt')

    sort_map = {
        "title_asc": "title",
        "title_desc": "-title",
        "year_asc": "release_year",
        "year_desc": "-release_year",
        "rating_asc": "rating",
        "rating_desc": "-rating",
    }

    order = sort_map.get(sort, "-id")

    qs = Review.objects.all()
    if search_txt:
        qs = qs.filter(
            Q(title__icontains=search_txt) |
            Q(director__icontains=search_txt) |
            Q(actors__icontains=search_txt))  # 제목, 감독, 배우로 검색
    

    if source == "tmdb":
        qs = qs.filter(is_from_tmdb=True)
    elif source == "user":
        qs = qs.filter(is_from_tmdb=False)

    reviews = qs.order_by(order)

    return render(request, "reviews/list.html", {"reviews": reviews, "sort": sort})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/detail.html", {"review": review})

def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("reviews:list")
    else:
        form = ReviewForm()
    return render(request, "reviews/form.html", {"form": form, "mode": "create"})

def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES, instance=review)
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
