from django.http import JsonResponse

def review_list(request):
    reviews = Review.objects.all()
    return render(request, "reviews/list.html", {"review" : reviews})