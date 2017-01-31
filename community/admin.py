from django.contrib import admin
from .models import Village, School, Student, Requirement, StudentNeed, StudentImage

# Register your models here.

admin.site.register(Village)
admin.site.register(School)
admin.site.register(Requirement)
admin.site.register(StudentNeed)
admin.site.register(StudentImage)


class StudentModelAdmin(admin.ModelAdmin):
    list_display = ["first_name", "display_name","last_updated", "published_date"]
    list_display_links = ["display_name"]
    list_filter = ["last_updated", "published_date"]
    search_fields = ["description"]

    class Meta:
        model=Student
admin.site.register(Student, StudentModelAdmin)
