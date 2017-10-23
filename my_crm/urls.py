from django.conf.urls import url, include
from my_crm import views

urlpatterns = [
    url(r'^$', views.index, name='sales_index'),
    url(r'^customers/$', views.customers, name='customers_index'),
    url(r'^customers/(\d+)/enrollment/$', views.enrollment, name='enrollment'),
    url(r'^customers/registration/(\d+)/(\w+)/$', views.stu_registration,name="stu_registration"),
    url(r'^contract_review/(\d+)/$', views.contract_review,name="contract_review"),
    url(r'^enrollment_rejection/(\d+)/$', views.enrollment_rejection,name="enrollment_rejection"),
    url(r'^payment/(\d+)/$', views.payment,name="payment"),
]
