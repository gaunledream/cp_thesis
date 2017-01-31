from django import forms
from django.forms import inlineformset_factory
from community.models import Village, School


class SchoolAddForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
                    'village',
                    'name',
                    'description',
                ]
        help_texts = {
                'name': '<--School where you studied & want to be part of!',
                'village': '<--Village where this school is!',
        }


class VillageAddForm(forms.ModelForm):
    class Meta:
        model = Village
        fields = [
                    'name',
                    'district',
                    'description',
                ]
SchoolAddFormSet = inlineformset_factory(Village, School, fields=('name', 'description',), extra=1, can_delete=False)
