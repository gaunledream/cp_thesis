"""trydjango19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import StudentDetailView, StudentListView, StudentNeedListView, StudentNeedDetailView, StudentCreateView, StudentUpdateView, StudentDeleteView, LocalStudentListView, StudentImageCreateView

urlpatterns = [
    url(r'^student/$', StudentListView.as_view(), name='student_list'),
    url(r'^student/(?P<pk>[0-9]+)/createimage$', StudentImageCreateView.as_view(), name='student_image'),
    url(r'^student/(?P<pk>[0-9]+)/addneeds$', StudentNeedListView.as_view(), name='studentneed_per_student'),
    url(r'^student/locals$', LocalStudentListView.as_view(), name='student_local_list'),
    url(r'^student/(?P<pk>\d+)/$', StudentDetailView.as_view(), name='student_detail'),
    url(r'^studentneeds/$', StudentNeedListView.as_view(), name='studentneed_list'),
    url(r'^studentneeds/(?P<pk>\d+)/$', StudentNeedDetailView.as_view(), name='studentneed_detail'),
    url(r'student/add/$', StudentCreateView.as_view(), name='student_add'),
    url(r'student/(?P<pk>[0-9]+)/update/$', StudentUpdateView.as_view(), name='student_update'),
    url(r'student/(?P<pk>[0-9]+)/delete/$', StudentDeleteView.as_view(), name='student_delete'),
]
