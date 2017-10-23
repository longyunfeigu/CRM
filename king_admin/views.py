from django.shortcuts import render, redirect, reverse, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from king_admin import king_admin
from king_admin.utils import table_filter, table_orderby, table_search
from king_admin.forms import create_model_form, PasswordForm
# from django.forms.boundfield import BoundField
# from django.contrib.auth.hashers import make_password


# Create your views here.

@login_required
def index(request):
    return render(request, 'king_admin/table_index.html', {'enabled_admin': king_admin.enabled_admin})

@login_required
def display_table_objects(request, app_name, table_name):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    contact_list, conditions = table_filter(request, admin_class) # 过滤
    contact_list = table_search(request, admin_class, contact_list) # 搜索
    contact_list, orderby_key = table_orderby(request, contact_list) # 排序
    paginator = Paginator(contact_list, admin_class.list_per_page) # 分页

    if request.method == 'POST':   # action 请求
        selected_ids = request.POST.get('selected_ids').split(',')
        action_func_str = request.POST.get('action')
        if hasattr(admin_class, action_func_str):
            action_func = getattr(admin_class, action_func_str)
            query_set = admin_class.model.objects.filter(id__in=selected_ids)
            request._action = action_func_str
            return action_func(admin_class, request, query_set)

    page = request.GET.get('page')
    try:
        query_set = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        query_set = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        query_set = paginator.page(paginator.num_pages)
    return render(request, 'king_admin/table_display.html',{'admin_class': admin_class,
                                                            'table_name': table_name,
                                                            'query_set': query_set,
                                                            'conditions': conditions,
                                                            'pre_orderby_key': request.GET.get('o', ''),
                                                            'orderby_key': orderby_key,
                                                            'search_value': request.GET.get('_q', ''),})
@login_required
def change_objects(request, app_name, table_name, nid):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    admin_class.add_form = False
    md_form_class = create_model_form(request, admin_class)
    obj = admin_class.model.objects.get(id=nid)
    if request.method == 'GET':
        md_form_obj = md_form_class(instance=obj)
    else:
        md_form_obj = md_form_class(request.POST, instance=obj)  # 更新
        if md_form_obj.is_valid():
            md_form_obj.save()
            return redirect(reverse(display_table_objects,args=[app_name, table_name]))
    return render(request, 'king_admin/change_objects.html', {'md_form_obj': md_form_obj, 'admin_class': admin_class,
                                                              'app_name': app_name, 'table_name': table_name,})

@login_required
def add_objects(request, app_name, table_name):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    admin_class.add_form = True
    md_form_class = create_model_form(request, admin_class)
    if request.method == 'GET':
        md_form_obj = md_form_class()
    else:
        md_form_obj = md_form_class(request.POST)   # 增加操作
        if md_form_obj.is_valid():
            try:
                md_form_obj.save()
            except Exception as e:
                errors = str(e)
                md_form_obj.add_error(errors.split('.')[-1], errors.split(':')[0])
            else:
                return redirect(request.path.replace('/add/', '/'))
    return render(request, 'king_admin/add_objects.html', {'md_form_obj': md_form_obj,
                                                           'admin_class': admin_class,
                                                           'app_name': app_name,
                                                           'table_name': table_name,
                                                           })

@login_required
def delete_objects(request, app_name, table_name, nid):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    obj = admin_class.model.objects.get(id=nid)
    if request.method == 'POST':
        obj.delete()
        return redirect('/king_admin/%s/%s/'%(app_name, table_name))
    return render(request, 'king_admin/delete_objects.html', {'objs': obj,
                                                              'app_name': app_name,
                                                              'table_name': table_name,})

@login_required
@login_required
def reset_password(request, app_name, table_name, nid):
    admin_class = king_admin.enabled_admin[app_name][table_name]
    obj = admin_class.model.objects.get(id=nid)
    if request.method == 'GET':
        password_form = PasswordForm()
        return render(request, 'king_admin/reset_password.html', {'obj': obj,
                                                                  'admin_class': admin_class,
                                                                  'password_form': password_form,
                                                                  })
    else:
        password_form = PasswordForm(request.POST)
        if password_form.is_valid():
            new_password = password_form.cleaned_data.get('new_password')
            obj.set_password(new_password)
            obj.save()
            return redirect(request.path.rstrip('password/'))
        else:
            import json
            return render(request, 'king_admin/reset_password.html', {'obj': obj,
                                                                        'admin_class': admin_class,
                                                                         'password_form': password_form,
                                            'errors': json.loads(password_form.errors.as_json()).get('__all__')[0].get('message')})
