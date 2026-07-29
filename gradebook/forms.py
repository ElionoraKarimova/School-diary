from django import forms
from .models import Grade


class GradeForm(forms.Form):
    student_id = forms.IntegerField()
    date = forms.DateField()
    value = forms.IntegerField(required=False, min_value=0, max_value=10)

class HomeworkForm(forms.Form):
    date = forms.DateField()
    task = forms.CharField(required=False, max_length=2000)