from reviews.models import Review

def review_to_document(review: Review) -> str:
    source = "TMDB" if review.is_from_tmdb else "USER"
    return f"""
제목: {review.title}
감독: {review.director}
출연: {review.actors}
장르: {review.genre}
개봉년도: {review.release_year}
별점: {review.rating}
출처: {source}
리뷰: {review.content}
""".strip()
