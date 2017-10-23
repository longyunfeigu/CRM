from django import template
from django.db.models import Sum

register = template.Library()


@register.simple_tag
def get_score(enroll_obj):
    study_records = enroll_obj.studyrecord_set.all().filter(course_record__from_class_id=enroll_obj.enrolled_class.id)
    return study_records.aggregate(Sum('score'))

@register.simple_tag
def get_date(studyrecord_date):
    return studyrecord_date.strftime('%Y-%m-%d')

@register.simple_tag
def has_homework(studyrecord_homework):
    if studyrecord_homework:
        return '有'
    else:
        return '无'
