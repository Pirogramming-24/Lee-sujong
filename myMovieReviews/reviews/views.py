from django.http import JsonResponse

def review_list(request):
    reviews = Review.objects.all()
    return render(request, "reviews/list.html", {"review" : reviews})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/detail.html", {"review": review})