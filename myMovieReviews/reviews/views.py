from django.shortcuts import render, get_object_or_404, redirect
from .models import Review
from .forms import ReviewForm

def review_list(request):
    reviews = Review.objects.all()
    return render(request, "reviews/list.html", {"review" : reviews})

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
    if request.method == "POST":
        form = ReviewForm(request.POST, instance = review)
        if form.is_valid():
            if form.is_valid():
                form.save()
                return redirect("reviews:list", pk=review.pk)
    else:
        form = ReviewForm(instance = review)
    return render(request, "reviews/form.html", {"form": form, "mode": "create"})