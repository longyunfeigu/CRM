from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import hashlib
import time
import os
from django.core.cache import cache
from django.conf import settings

from my_crm import models
from my_crm import forms as myForm
from utils.message import sendMessage
# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def customers(request):
    return render(request, 'sales/customers.html')


@login_required
def enrollment(request, nid):
    customer_obj = models.Customer.objects.get(id=nid)
    email = customer_obj.email
    msg = ''
    if request.method == 'GET':
        enroll_form = myForm.EnrollmentForm()
    else:
        enroll_form = myForm.EnrollmentForm(request.POST)
        if enroll_form.is_valid():
            enroll_form.cleaned_data['customer'] = customer_obj
            content = '<a href="http://localhost:8000/crm/customers/registration/{enroll_obj_id}/{random_str}/">请点该链接</a>'
            try:
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)
                hashmd5 = hashlib.md5(email.encode('utf8'))
                hashmd5.update(str(time.time()).encode('utf8'))
                random_str = hashmd5.hexdigest()
                cache.set(enroll_obj.id, random_str, 600)
                content = content.format(enroll_obj_id=enroll_obj.id, random_str=random_str)
                # print(content)
                sendMessage('学员注册链接', content, email)
                msg = '链接已发送给学员，请通知学员进行注册'
            except IntegrityError as e:
                enroll_form.add_error('__all__', '* 该用户的此条报名信息已存在，不能重复创建')
                enroll_obj = models.Enrollment.objects.filter(customer=customer_obj,
                                                              enrolled_class=enroll_form.cleaned_data['enrolled_class']).first()
                if enroll_obj.contract_agreed:
                    return redirect("/crm/contract_review/%s/"%enroll_obj.id)
                hashmd5 = hashlib.md5(email.encode('utf8'))
                hashmd5.update(str(time.time()).encode('utf8'))
                random_str = hashmd5.hexdigest()
                cache.set(enroll_obj.id, random_str, 600)
                content = content.format(enroll_obj_id=enroll_obj.id, random_str=random_str)
                # print(content)
                sendMessage('学员注册链接', content, email)
                msg = '链接已发送给学员，请通知学员进行注册'
        else:
            pass
    return render(request, 'sales/enrollment.html', {'enroll_form': enroll_form,
                                                     'customer_obj': customer_obj,
                                                     'msg': msg,})

def stu_registration(request, enroll_id, random_str):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    if cache.get(enroll_id) == random_str:
        if request.method == 'GET':
            customer_form = myForm.CustomerForm(instance=enroll_obj.customer)
            if enroll_obj.contract_agreed:
                status = 1
            else:
                status = 0
        else:
            if request.is_ajax():
                enroll_data_dir = "%s/%s" % (settings.ENROLLED_DATA, enroll_id)
                if not os.path.exists(enroll_data_dir):
                    os.makedirs(enroll_data_dir, exist_ok=True)

                for k, file_obj in request.FILES.items():
                    with open("%s/%s" % (enroll_data_dir, file_obj.name), "wb") as f:
                        for chunk in file_obj.chunks():
                            f.write(chunk)
                return HttpResponse("success")
            customer_form = myForm.CustomerForm(request.POST, instance=enroll_obj.customer)
            if customer_form.is_valid():
                customer_form.save()
                enroll_obj.contract_agreed = True
                enroll_obj.save()
                status = 1
                return render(request, "sales/stu_registration.html", {"status": status})
            else:
                status = 0
        return render(request, 'sales/stu_registration.html', {'customer_form': customer_form,
                                                               'enroll_obj': enroll_obj,
                                                               'status': status, })
    else:
        return render(request, 'sales/invalid.html')

def contract_review(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_form = myForm.EnrollmentForm(instance=enroll_obj)
    customer_form = myForm.CustomerForm(instance=enroll_obj.customer)
    return render(request, 'sales/contract_review.html', {'enroll_form': enroll_form,
                                                          'customer_form': customer_form,
                                                          'enroll_obj': enroll_obj,})

def payment(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    errors = []
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            amount = int(amount)
            if amount < 1000:
                errors.append('"缴费金额不得低于1000元"')
            else:
                enroll_obj.contract_approved = True
                enroll_obj.save()
                models.Payment.objects.create(customer=enroll_obj.customer,
                                              course=enroll_obj.enrolled_class.course,
                                              amount=amount,
                                              consultant=enroll_obj.consultant)
                enroll_obj.customer.status = 0
                enroll_obj.customer.save()
                return render(request, 'sales/success.html')
        else:
            errors.append('"缴费金额不得低于1000元"')

    return render(request, 'sales/payment.html', {'enroll_obj': enroll_obj,
                                                  'errors': errors, })

def enrollment_rejection(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()
    return redirect("/crm/customers/%s/enrollment/" % enroll_obj.customer.id)