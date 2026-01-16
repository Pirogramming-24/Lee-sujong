import json
from django.shortcuts import render, redirect
from .forms import PostForm, NutritionForm
from .models import NutritionInfo, Post
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .services.ocr_service import run_ocr
from .services.rules import extract_nutrition

# Create your views here.
def main(request):
    posts = Post.objects.all()

    search_txt = request.GET.get('search_txt')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if search_txt:
        posts = posts.filter(title__icontains=search_txt)  # 대소문자 구분 없이 검색
    
    try:
        if min_price:
            posts = posts.filter(price__gte=int(min_price))
        if max_price:
            posts = posts.filter(price__lte=int(max_price))
    except (ValueError, TypeError):
        pass  # 필터를 무시하되, 기존 검색 필터를 유지

    context = {
        'posts': posts,
        'search_txt': search_txt,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'posts/list.html', context=context)

def create(request):
    if request.method == 'GET':
        post_form = PostForm()
        nutrition_form = NutritionForm()
        return render(request, 'posts/create.html', {
            'post_form': post_form,
            'nutrition_form': nutrition_form,
        })
    else:
        post_form = PostForm(request.POST, request.FILES)
        nutrition_form = NutritionForm(request.POST)

        if post_form.is_valid() and nutrition_form.is_valid():
            post = post_form.save()

            nutrition = nutrition_form.save(commit=False)
            nutrition.post = post
            nutrition.save()

            return redirect('/')

        return render(request, 'posts/create.html', {
            'post_form': post_form,
            'nutrition_form': nutrition_form,
        })

def detail(request, pk):
    target_post = Post.objects.get(id = pk)
    context = { 'post': target_post }
    return render(request, 'posts/detail.html', context=context)

def update(request, pk):
    post = Post.objects.get(id=pk)

    # ✅ post에 연결된 NutritionInfo 가져오기 (없으면 새로 만들 준비)
    nutrition = getattr(post, "nutrition", None)

    if request.method == 'GET':
        post_form = PostForm(instance=post)
        nutrition_form = NutritionForm(instance=nutrition)

        return render(request, 'posts/update.html', {
            'post_form': post_form,
            'nutrition_form': nutrition_form,
            'post': post,
        })

    # POST
    post_form = PostForm(request.POST, request.FILES, instance=post)
    nutrition_form = NutritionForm(request.POST, instance=nutrition)

    if post_form.is_valid() and nutrition_form.is_valid():
        post_form.save()

        n = nutrition_form.save(commit=False)
        n.post = post
        n.save()

        return redirect('posts:detail', pk=pk)

    return render(request, 'posts/update.html', {
        'post_form': post_form,
        'nutrition_form': nutrition_form,
        'post': post,
    })


def delete(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('/')

@require_POST
@csrf_protect
def ocr_preview(request):
    if "nutrition_image" not in request.FILES:
        return JsonResponse({"ok": False, "error": "nutrition_image가 필요합니다."}, status=400)

    f = request.FILES["nutrition_image"]
    file_bytes = f.read()

    try:
        text = run_ocr(file_bytes)
        nutrition = extract_nutrition(text)
        return JsonResponse({"ok": True, "nutrition": nutrition})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
    