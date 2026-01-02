from django import forms
from .models import DevTool

class DevToolForm(forms.ModelForm):
    class Meta:
        model = DevTool
        fields = [
            "name",
            "kind",
            "content",
        ]
        labels = {
            "name": "이름",
            "kind": "종류",
            "content": "개발툴 설명"
        }