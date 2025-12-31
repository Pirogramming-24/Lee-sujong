from django.shortcuts import render, get_object_or_404, redirect
from .models import Review
from .forms import ReviewForm

def review_list(request):
    reviews = Review.objects.all()
    return render(request, "reviews/list.html", {"review" : reviews})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, "reviews/detail.html", {"review": review})