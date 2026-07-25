from django import template

register = template.Library()

@register.simple_tag
def get_grade(grade_map, student_id, date_obj):

    date_str = date_obj.strftime('%Y-%m-%d')
    grade = grade_map.get((student_id, date_str))
    return grade.value if grade else ''


@register.simple_tag
def get_hw(hw_map, date_obj):

    date_str = date_obj.strftime('%Y-%m-%d')
    return hw_map.get(date_str, '')