from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import FieldDoesNotExist
from django.utils.timezone import datetime, timedelta
from django.db.models.query import QuerySet

register = template.Library()

@register.simple_tag
def display_table_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def render_table_tr(request, obj, admin_class):
    ele = '<tr><td><input type="checkbox" value="%s"></td>'%obj.id
    for index,column in enumerate(admin_class.list_display):
        try:
            field_obj = obj._meta.get_field(column)
            if field_obj.choices:
                td_data = getattr(obj, 'get_%s_display'%column)()
            else:
                td_data = getattr(obj, column)
            if type(field_obj).__name__ == 'DateTimeField':
                td_data = getattr(obj, column).strftime('%Y-%m-%d %H:%M')
            if index == 0:
                td_data = '<a href="{request_path}{obj_id}/change">{data}</a>'.format(request_path=request.path, obj_id=obj.id, data=td_data)
        except FieldDoesNotExist as e:
            column_func = getattr(admin_class, column)
            admin_class.obj = obj
            td_data = column_func()
        ele += '<td>%s</td>'%td_data
    ele += '</tr>'
    return mark_safe(ele)
"""
@register.simple_tag
def render_page_num(loop, query_set, conditions):
    page_href_supply = ''
    for k,v in conditions.items():
        page_href_supply += '&%s=%s'%(k, v)

    if abs(loop - query_set.number) <= 2:
        active = ''
        if loop == query_set.number:
            active = 'active'
        li_ele = '<li class="%s"><a href="?page=%s%s">%s</a></li>'%(active, loop, page_href_supply, loop)
        return mark_safe(li_ele)
    return ''

{% for loop in query_set.paginator.page_range %}
    {% render_page_num loop query_set conditions %}
{% endfor %}
"""

@register.simple_tag
def render_all_page(query_set, conditions, pre_orderby_key):
    # page_href_supply = ''
    # for k, v in conditions.items():
    #     page_href_supply += '&%s=%s' % (k, v)
    page_href_supply = get_conditions(conditions)

    all_li_ele = ''
    add_dot = True
    for loop in query_set.paginator.page_range:
        active = ''
        if loop <= 2 or loop > query_set.paginator.num_pages - 2:
            if loop == query_set.number:
                active = 'active'
            all_li_ele += '<li class="%s"><a href="?page=%s%s">%s</a></li>' % (active, loop, page_href_supply, loop)
        elif abs(loop - query_set.number) <= 1:
            if loop == query_set.number:
                add_dot = True
                active = 'active'
            all_li_ele += '<li class="%s"><a href="?page=%s%s&%s">%s</a></li>' % (active, loop, page_href_supply, pre_orderby_key, loop)
        else:
            if add_dot:
                all_li_ele += '<li><a>...</a></li>'
                add_dot = False
    return mark_safe(all_li_ele)

@register.simple_tag
def render_select(conditions, filter, admin_class):
    filter_val = conditions.get(filter)
    #select_ele = '<label class="">%s</label><select class="form-control" name="%s"><option value="">----</option>'%(filter,filter)
    select_ele = '''<label class="">{filter_name}</label><select class="form-control" name='{filter}' ><option value=''>----</option>'''
    field_obj = admin_class.model._meta.get_field(filter)
    if field_obj.choices:
        for item in field_obj.choices:
            selected = ''
            if filter_val == str(item[0]):
                selected = 'selected'
            select_ele += '<option %s value="%s">%s</option>'%(selected, item[0], item[1])
    if type(field_obj).__name__ == 'ForeignKey':
        for item in field_obj.get_choices()[1:]:
            selected = ''
            if filter_val == str(item[0]):
                selected = 'selected'
            select_ele += '<option %s value="%s">%s</option>' % (selected, item[0], item[1])
    if type(field_obj).__name__ in ['DateTimeField', 'DateField']:
        filter_val = conditions.get('%s__gte'%filter)
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['今天', datetime.now().date()])
        date_els.append(["昨天", today_ele - timedelta(days=1)])
        date_els.append(["近7天", today_ele - timedelta(days=7)])
        date_els.append(["本月", today_ele.replace(day=1)])
        date_els.append(["近30天", today_ele - timedelta(days=30)])
        date_els.append(["近90天", today_ele - timedelta(days=90)])
        date_els.append(["近180天", today_ele - timedelta(days=180)])
        date_els.append(["本年", today_ele.replace(month=1, day=1)])
        date_els.append(["近一年", today_ele - timedelta(days=365)])
        for item in date_els:
            selected = ''
            if filter_val == str(item[1]):
                selected = 'selected'
            select_ele += '''<option value='%s' %s>%s</option>''' % (item[1], selected, item[0])
        filter_field_name = "%s__gte" % filter
    else:
        filter_field_name = filter
    select_ele += '</select>'
    select_ele = select_ele.format(filter=filter_field_name, filter_name=filter)
    return mark_safe(select_ele)

@register.simple_tag
def get_conditions(conditions):
    page_href_supply = ''
    for k, v in conditions.items():
        page_href_supply += '&%s=%s' % (k, v)
    return page_href_supply


@register.simple_tag
def render_th(field, orderby_key, conditions, admin_class):
    conditions = get_conditions(conditions)
    th_ele = '<a href="?o={orderby_key}{conditions}">{field}</a>{sort_icon}'
    if orderby_key:
        # 根据返回的排序key来决定符号
        if orderby_key.startswith('-'):
            sort_icon = '↑'
        else:
            sort_icon = '↓'
        # 判断哪个字段排序了，然后更改该字段的 a 标签的 href 属性
        if orderby_key.strip('-') == field:
            orderby_key = orderby_key
        else:
            orderby_key = field
            sort_icon = ''

    # 没有排序，原始状态
    else:
        orderby_key = field
        sort_icon = ''
    try:
        column_verbose_name = admin_class.model._meta.get_field(field).verbose_name.upper()
    except FieldDoesNotExist as e:
        if hasattr(admin_class, field):
            column_func = getattr(admin_class, field)

            if hasattr(column_func, 'short_description'):
                column_verbose_name = column_func.short_description.upper()
            else:
                column_verbose_name = field.upper()
            th_ele = '<a href="javascript:void(0)">%s</a>'%column_verbose_name
            return mark_safe(th_ele)
    th_ele = th_ele.format(orderby_key=orderby_key, field=column_verbose_name, sort_icon=sort_icon, conditions=conditions)
    return mark_safe(th_ele)

@register.simple_tag
def get_m2m_obj_list(admin_class, field, md_form_obj):
    field_obj = getattr(admin_class.model, field.name)
    if md_form_obj.instance.id:
        selected_tags = get_m2m_selected_obj_list(md_form_obj, field)
        unselected_tags = field_obj.rel.to.objects.exclude(id__in=selected_tags)
        return unselected_tags
    else:
        return field_obj.rel.to.objects.all()

@register.simple_tag
def get_m2m_selected_obj_list(md_form_obj, field):
    if md_form_obj.instance.id:
        field_obj = getattr(md_form_obj.instance, field.name)
        return field_obj.all()

def recursive_related_objs_lookup(objs):
    #model_name = objs[0]._meta.model_name
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li> %s: %s </li>'''%(obj._meta.verbose_name,obj.__str__().strip("<>"))
        ul_ele += li_ele

        #for local many to many
        #print("------- obj._meta.local_many_to_many", obj._meta.local_many_to_many)
        for m2m_field in obj._meta.local_many_to_many: #把所有跟这个对象直接关联的m2m字段取出来了
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj,m2m_field.name) #getattr(customer, 'tags')
            for o in m2m_field_obj.select_related():# customer.tags.select_related()
                li_ele = '''<li> %s: %s </li>''' % (m2m_field.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele +=li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele  #最终跟最外层的ul相拼接


        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():

                if hasattr(obj, related_obj.get_accessor_name()):  # hassattr(customer,'enrollment_set')
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())
                    print("-------ManyToManyRel",accessor_obj,related_obj.get_accessor_name())
                    # 上面accessor_obj 相当于 customer.enrollment_set
                    if hasattr(accessor_obj, 'select_related'):  # slect_related() == all()
                        target_objs = accessor_obj.select_related()  # .filter(**filter_coditions)
                        # target_objs 相当于 customer.enrollment_set.all()

                        sub_ul_ele ="<ul style='color:red'>"
                        for o in target_objs:
                            li_ele = '''<li> %s: %s </li>''' % (o._meta.verbose_name, o.__str__().strip("<>"))
                            sub_ul_ele += li_ele
                        sub_ul_ele += "</ul>"
                        ul_ele += sub_ul_ele

            elif hasattr(obj,related_obj.get_accessor_name()): # hassattr(customer,'enrollment_set')
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                #上面accessor_obj 相当于 customer.enrollment_set
                if hasattr(accessor_obj,'select_related'): # slect_related() == all()
                    target_objs = accessor_obj.select_related() #.filter(**filter_coditions)
                    # target_objs 相当于 customer.enrollment_set.all()
                else:
                    print("one to one i guess:",accessor_obj)
                    target_objs = accessor_obj

                if len(target_objs) >0:
                    #print("\033[31;1mdeeper layer lookup -------\033[0m")
                    #nodes = recursive_related_objs_lookup(target_objs,model_name)
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele +="</ul>"
    return ul_ele

@register.simple_tag
def display_obj_related(objs):
    '''把对象及所有相关联的数据取出来'''
    if not isinstance(objs, QuerySet):
        objs = [objs,]     #fake
    if objs:
        return mark_safe(recursive_related_objs_lookup(objs))

@register.simple_tag
def get_action_verbose_name(action, admin_class):
    action_func = getattr(admin_class, action)
    return action_func.short_description if hasattr(action_func, 'short_description') else action

@register.simple_tag
def get_mdform_errors(md_form_obj):
    import json
    return json.loads(md_form_obj.errors.as_json()).get('__all__')