from django.db.models import Q

def table_filter(request,admin_class):
    conditions = {}
    keywords = ['page', 'o', '_q']
    for k,v in request.GET.items():
        if k in keywords:
            continue
        if v:
            conditions[k] = v
    return admin_class.model.objects.filter(**conditions).order_by('-%s'%admin_class.ordering if admin_class.ordering else '-id'), conditions

def table_orderby(request, contact_list):
    orderby_key = request.GET.get('o')
    if orderby_key:
        res = contact_list.order_by(orderby_key)
        if orderby_key.startswith('-'):
            orderby_key = orderby_key.strip('-')
        else:
            orderby_key = '-%s'%orderby_key
    else:
        res = contact_list
    return res, orderby_key

def table_search(request, admin_class, contact_list):
    _q = request.GET.get('_q')
    if _q:
        q = Q()
        q.connector = 'OR'
        for search_field in admin_class.search_fields:
            q.children.append(('%s__icontains'%search_field, _q))
        contact_list = contact_list.filter(q)
    return contact_list

