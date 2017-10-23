from django.conf.urls import url, include
from king_admin import views

urlpatterns = [
    url(r'^$', views.index, name='table_index'),
    url(r'^(\w+)/(\w+)/$', views.display_table_objects, name='display_table_objects'),
    url(r'^(\w+)/(\w+)/(\d+)/change/$', views.change_objects, name='change_objects'),
    url(r'^(\w+)/(\w+)/(\d+)/change/password/$', views.reset_password, name='reset_password'),
    url(r'^(\w+)/(\w+)/add/$', views.add_objects, name='add_objects'),
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.delete_objects, name='delete_objects'),
]
