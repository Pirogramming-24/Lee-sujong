from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ("tmdb_id", "is_from_tmdb", "created_at", "updated_at")