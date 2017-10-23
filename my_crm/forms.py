from django.forms import ModelForm
from django.forms import ValidationError

from my_crm import models

class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            if type(field_obj).__name__ != 'BooleanField':
                field_obj.widget.attrs['class'] = 'form-control'
        return ModelForm.__new__(cls)

    class Meta:
        model = models.Enrollment
        fields = ("enrolled_class","consultant")

class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            if type(field_obj).__name__ != 'BooleanField':
                field_obj.widget.attrs['class'] = 'form-control'
            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'
        return ModelForm.__new__(cls)
    class Meta:
        model = models.Customer
        fields = '__all__'
        exclude = ['tags', 'content', 'memo', 'status', 'referral_from', 'consult_course']
        readonly_fields = [ 'qq','consultant','source']

    def clean(self):
        for field_name in CustomerForm.Meta.readonly_fields:
            if getattr(self.instance, field_name) != self.cleaned_data.get(field_name):
                raise ValidationError('只读字段不能修改')
                #self.add_error('__all__', '只读字段不能修改')
        return self.cleaned_data



