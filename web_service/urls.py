from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('contacts/', get_contacts, name='contacts'),
    re_path(r'^task/(?P<task_id>(\w|\.|-|:)+)/$', TaskManager.as_view(), name='task_handler'),
    path('task/', TasksManager.as_view(), name='tasks_handler'),
]
