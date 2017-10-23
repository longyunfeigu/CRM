from django.forms import ModelForm
from django.forms import forms
from django.forms import fields
from django.forms import widgets
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.core.validators import RegexValidator

from utils.captcha.mycaptcha import Captcha


def create_model_form(request, admin_class):
    class DynamicModelForm(ModelForm):
        class Meta:
            model = admin_class.model
            fields = '__all__'
            exclude = admin_class.modelform_exclude_fields
        def __new__(cls, *args, **kwargs):
            for field_name, field_obj in cls.base_fields.items():
                if type(field_obj).__name__ != 'BooleanField':
                    field_obj.widget.attrs['class'] = 'form-control'
                if admin_class.readonly_table:
                    field_obj.widget.attrs['disabled'] = 'disabled'
                else:
                    if field_name in admin_class.readonly_fields and not admin_class.add_form:
                        field_obj.widget.attrs['disabled'] = 'disabled'
                if hasattr(admin_class, 'clean_%s'%field_name):
                    field_clean_func = getattr(admin_class, 'clean_%s'%field_name)
                    setattr(cls, 'clean_%s'%field_name, field_clean_func)
            return ModelForm.__new__(cls)
        def clean(self):
            error_list = []
            if self.instance.id:     # 表名这是一个修改的表单
                for field_name in admin_class.readonly_fields:
                    db_field_val = getattr(self.instance, field_name)
                    if hasattr(db_field_val, 'select_related'):
                        m2m_objs = db_field_val.select_related()
                        if set(m2m_objs) != set(self.cleaned_data['tags']):
                            error_list.append(ValidationError(
                                _('Field %(field)s is readonly'),
                                code='invalid',
                                params={'field': field_name},
                            ))
                        continue
                    front_field_val = self.cleaned_data.get(field_name)
                    if front_field_val != db_field_val:
                        error_list.append(ValidationError(
                            _('Field %(field)s is readonly'),
                            code='invalid',
                            params={'field': field_name},
                        ))
            if admin_class.readonly_table:
                raise ValidationError(
                    _('Table is  readonly,cannot be modified or added'),
                    code='invalid'
                )
            response = admin_class.default_mdform_validation(self)
            if response:
                error_list.append(response)
            if error_list:
                raise ValidationError(error_list)

    return DynamicModelForm
    # class Meta:
    #     model = admin_class.model
    #     fields = '__all__'
    # attrs = {'Meta': Meta}
    # _model_form = type('DynamicModelForm', (ModelForm,), attrs)
    # return _model_form

class PasswordForm(forms.Form):
    new_password = fields.CharField(widget=widgets.PasswordInput(attrs={
        'class': "form-control", 'name': 'new_password', 'id': 'new_password', 'placeholder': '请输入新密码',
    }), min_length=8, max_length=32,
        help_text=mark_safe("密码最少8位，最多32位<br/>密码不能是单纯的字母或数字"),
    )
    new_password_confirm = fields.CharField(widget=widgets.PasswordInput(attrs={
        'class': "form-control", 'name': 'new_password_confirm', 'id': 'new_password_confirm', 'placeholder': '请再次输入新密码',
    }), min_length=8, max_length=32)

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password.isdigit() or new_password.isalpha():
            #raise ValidationError('密码不能是单纯的数字或字母', 'invalid')
            self.add_error('__all__', '密码不能是单纯的数字或字母')
        return new_password

    def clean(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_confirm = self.cleaned_data.get('new_password_confirm')
        if new_password != new_password_confirm:
            #raise ValidationError('两次新密码输入不一致', 'invalid')
            self.add_error('__all__', '两次新密码输入不一致')
        return self.cleaned_data

class LoginForm(forms.Form):
    email = fields.CharField(widget=widgets.TextInput(attrs={
        'class': "form-control",'name': 'email', 'id': 'email', 'placeholder': '请输入邮箱',
         'autofocus': 'autofocus'
    }))
    password = fields.CharField(widget=widgets.PasswordInput(attrs={
        'class': "form-control",'name': 'password', 'id': 'password', 'placeholder': '请输入密码',
    }))

    captcha = fields.CharField(widget=widgets.TextInput(attrs={
        'class': "form-control", 'name': 'captcha', 'id': 'captcha', 'placeholder': '请输入验证码',
    }))
    remember = fields.BooleanField(required=False, widget=widgets.CheckboxInput(attrs={
        'name': 'remember','id': 'remember'
    }))

    def clean_captcha(self):
        captcha = self.cleaned_data['captcha']
        if not Captcha.check_captcha(captcha):
            raise ValidationError('验证码错误')
        return captcha