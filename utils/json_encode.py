import json
from django.core.exceptions import ValidationError

class JsonCustomEncode(json.JSONEncoder):
    def default(self, field):
        if isinstance(field, ValidationError):
            return {'code': field.code, 'message': field.message}
        else:
            return super(JsonCustomEncode, self).default(field)