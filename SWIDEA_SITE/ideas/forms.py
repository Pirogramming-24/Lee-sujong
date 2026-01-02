from django import forms
from .models import Idea

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = [
            "title",
            "image",
            "content",
            "devtool",
        ]
        labels = {
            "title": "아이디어 제목",
            "content": "설명",
            "devtool": "사용 개발툴",
        }
        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 8,          # 줄 수
                "class": "form-textarea",
            }),
        }