from django import forms
from .models import Post        
from django.forms import SelectDateWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields=[
            "title",
            "image",
            "content",
            "draft",
            "publish",
            "posts_for_village",
            "posts_for_school",
            "public",
        ]
        widgets = {
            'publish': SelectDateWidget(
                empty_label=("Choose Year", "Choose Month", "Choose Day"),
            ),
        }