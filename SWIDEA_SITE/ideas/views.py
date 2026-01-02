from django.shortcuts import render, redirect, get_object_or_404
from .models import Idea, IdeaStar
from .forms import IdeaForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

def main(request):
    sort = request.GET.get("sort", "star")

    qs = Idea.objects.select_related("devtool")

    paginator = Paginator(qs, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "ideas/main.html", {
        "page_obj": page_obj,
    })

def idea_create(request):
    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save()
            IdeaStar.objects.get_or_create(idea=idea)
            return redirect("ideas:detail", pk=idea.pk)  
    else:
        form = IdeaForm()

    return render(request, "ideas/form.html", {"form": form, "mode": "create"})

def idea_detail(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    star, _ = IdeaStar.objects.get_or_create(idea=idea)
    return render(request, "ideas/detail.html", {"idea": idea, "star": star})

def idea_update(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            form.save()
            return redirect("ideas:detail", pk=idea.pk)
    else:
        form = IdeaForm(instance=idea)

    return render(request, "ideas/form.html", {"form": form, "mode": "update", "idea": idea})

def idea_delete(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    if request.method == "POST":
        idea.delete()
    return redirect("home")

@require_POST
def idea_toggle_star(request, pk):
    idea = get_object_or_404(Idea, pk=pk)
    star, _ = IdeaStar.objects.get_or_create(idea=idea)

    star.is_starred = not star.is_starred
    star.save()

    return JsonResponse({"starred": star.is_starred})

@require_POST
def idea_interest(request, pk):
    idea = get_object_or_404(Idea, pk=pk)

    delta = int(request.POST.get("delta", 0))
    idea.interest = max(0, idea.interest + delta)
    idea.save()

    return JsonResponse({"interest": idea.interest})