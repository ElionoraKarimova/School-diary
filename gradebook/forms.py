from django import forms
from .models import Schedule

class GradeForm(forms.Form):
    student_id = forms.IntegerField()
    date = forms.DateField()
    value = forms.IntegerField(required=False, min_value=0, max_value=10)


class HomeworkForm(forms.Form):
    date = forms.DateField()
    task = forms.CharField(required=False, max_length=2000)

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["group", "subject", "teacher", "weekday", "lesson_number", "classroom"]
