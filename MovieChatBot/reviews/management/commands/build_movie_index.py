from django.core.management.base import BaseCommand
from reviews.models import Review
from reviews.rag.document import review_to_document
from reviews.rag.index import save_index

class Command(BaseCommand):
    help = "Build FAISS index from Review DB"

    def handle(self, *args, **options):
        reviews = Review.objects.all()

        texts = []
        metas = []

        for r in reviews:
            doc = review_to_document(r)

            texts.append(doc)
            metas.append({
                "id": r.id,
                "title": r.title,
                "director": r.director,
                "actors": r.actors,
                "genre": r.genre,
                "release_year": r.release_year,
                "rating": str(r.rating),  
                "is_from_tmdb": r.is_from_tmdb,
                "doc": doc,  
            })

        save_index(texts, metas)
        self.stdout.write(self.style.SUCCESS("FAISS index built successfully"))
