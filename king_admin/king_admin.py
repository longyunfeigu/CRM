from my_crm import models
from django.shortcuts import render, redirect, reverse,HttpResponse
from django.forms import ValidationError
from django.utils.translation import ugettext as _

enabled_admin = {}

class BaseAdmin(object):
    list_display = []
    list_filter = []
    list_per_page = 20
    search_fields = []
    filter_horizontal = []
    ordering = None
    readonly_fields = []
    readonly_table = False
    actions = ['delete_selected_objs',]
    modelform_exclude_fields = []
    def delete_selected_objs(self, request, queryset):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        selected_ids = ','.join([str(i.id) for i in queryset])
        action = request._action
        delete_confirm = request.POST.get('delete_confirm')
        if delete_confirm == 'yes':
            queryset.delete()
            return redirect(request.path)
        return render(request, 'king_admin/delete_objects.html', {'objs': queryset,
                                                                  'app_name': app_name,
                                                                  'table_name': table_name,
                                                                  'selected_ids': selected_ids,
                                                                  'action': action,})
    def default_mdform_validation(self):
        """用户可以在此进行自定义的表单验证，相当于django form的clean方法"""
        pass


class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name','source','consult_course','consultant','date', 'status', 'enroll']
    list_per_page = 6
    list_filter = ['source','consultant','consult_course','status', 'date']
    search_fields = ['qq', 'name', 'consultant__name']
    filter_horizontal = ['tags']
    actions = ['delete_selected_objs', 'ceshi']
    readonly_fields = ["qq", "consultant", "tags"]
    # readonly_table = True
    def ceshi(self, request, queryset):
        print('自定义ceshi')
    ceshi.short_description = '测试'

    def enroll(self):
        if self.obj.status == 0:   # 已报名
            enroll_msg = '报名新课程'
        else:
            enroll_msg = '报名'
        return '<a href="/crm/customers/%s/enrollment">%s</a>'%(self.obj.id,enroll_msg)

    enroll.short_description = '报名链接'

    def default_mdform_validation(self):
        consult_content = self.cleaned_data.get("content", '')
        if len(consult_content) < 10:
            return ValidationError(_('Field %(field)s must has least 10 characters'),
                            code='invalid',
                            params={'field': 'content'},
                        )
    def clean_name(self):
        name = self.cleaned_data.get("name", '')
        if not name:
            self.add_error('name','cannot be null')

class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['customer', 'consultant', 'date']

class UserProfileAdmin(BaseAdmin):
    list_display = ['email', 'name']
    readonly_fields = ('password','email')
    modelform_exclude_fields = ['last_login']

def register(model, admin_class=None):
    if model._meta.app_label not in enabled_admin:
        enabled_admin[model._meta.app_label] = {}
    admin_class.model = model
    enabled_admin[model._meta.app_label][model._meta.model_name] = admin_class

class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']
    def initialize_studyrecords(self, request, queryset):
        print('--->initialize_studyrecords',self,request,queryset)
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            new_obj_list.append(models.StudyRecord(
                student=enroll_obj,
                course_record=queryset[0],
                attendance=0,
                score=0,
            ))
        try:
            models.StudyRecord.objects.bulk_create(new_obj_list) #批量创建
        except Exception as e:
            return HttpResponse("批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录")
        return redirect("/king_admin/my_crm/studyrecord/?course_record=%s"%queryset[0].id )
    initialize_studyrecords.short_description = "初始化本节所有学员的上课记录"
    actions = ['delete_selected_objs', 'initialize_studyrecords',]
# Now register the new UserAdmin...

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record','attendance','score','date']
    list_filter = ['course_record','score','attendance']
    list_editable = ['score','attendance']

register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.StudyRecord, StudyRecordAdmin)
register(models.CourseRecord, CourseRecordAdmin)