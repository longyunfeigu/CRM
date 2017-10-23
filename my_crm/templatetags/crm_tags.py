from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import FieldDoesNotExist
from django.utils.timezone import datetime, timedelta
from django.db.models.query import QuerySet

register = template.Library()


@register.simple_tag
def get_mdform_errors(md_form_obj):
    import json
    return json.loads(md_form_obj.errors.as_json()).get('__all__')