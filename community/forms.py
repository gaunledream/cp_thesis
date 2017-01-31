from django import forms
from .models import Student, StudentNeed, StudentImage


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields=["first_name","last_name","display_name", "village", "grade",
                "is_public",  "show_full_name", "description"]


class StudentImageForm(forms.ModelForm):
    class Meta:
        model = StudentImage
        fields=["image"]


def create_model_form(user):
    """Returns a new model form for this user"""

    class StudentNeedForm(forms.ModelForm):
        class Meta:
            model = StudentNeed
            fields=["need","student", "target","measurement", "description"]
        #field1 = forms.ModelChoiceField(queryset=..., empty_label="(Nothing)")

        def __init__(self, *args, **kwargs):
            super(StudentNeedForm, self).__init__(*args, **kwargs)
            self.fields['student'].queryset=Student.objects.filter(school=user.school)
    return StudentNeedForm

