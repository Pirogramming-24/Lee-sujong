from django.shortcuts import render, redirect, get_object_or_404
from .models import DevTool
from .forms import DevToolForm

def main(request):
    devtools = DevTool.objects.all()
    return render(request, "devtools/main.html", {"devtools": devtools})

def devtool_create(request):
    if request.method == "POST":
        form = DevToolForm(request.POST)
        if form.is_valid():
            devtool = form.save()
            return redirect("devtools:detail", pk=devtool.pk)
    else:
        form = DevToolForm()
    
    return render(request, "devtools/form.html", {"form": form, "mode": "create"})

def devtool_detail(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    ideas = devtool.ideas.all()   # Idea.devtool FK에 related_name="ideas"일 때
    return render(request, "devtools/detail.html", {"devtool": devtool, "ideas": ideas})

def devtool_update(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)

    if request.method == "POST":
        form = DevToolForm(request.POST, instance=devtool)
        if form.is_valid():
            devtool = form.save()
            return redirect("devtools:detail", pk=devtool.pk)
    else:
        form = DevToolForm(instance=devtool)
    
    return render(request, "devtools/form.html", {"form": form, "mode": "update", "devtool": devtool})

def devtool_delete(request, pk):
    devtool = get_object_or_404(DevTool, pk=pk)
    if request.method == "POST":
        devtool.delete()
    return redirect("devtools:main")