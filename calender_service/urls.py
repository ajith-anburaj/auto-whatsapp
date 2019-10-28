from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', get_calenders, name='calender'),
    re_path(r'^event/(?P<calender>(\w|\.|-|#|@)+)/$', get_events, name='events')
]
