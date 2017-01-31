from django.contrib import admin

# Register your models here.
from .models import Post


class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "updated","timestamp", "user"]
    list_display_links = ["updated"]
    list_filter = ["timestamp", "updated", "user"]
    search_fields = ["content"]

    class Meta:
        model = Post

admin.site.register(Post, PostModelAdmin)
