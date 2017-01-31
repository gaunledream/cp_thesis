from django.conf.urls import url
from .views import ProfileDetailView, LoginView, AboutView, contact, home, logout, VillageUpdateView, SchoolAddressUpdateView #VillageAddressCreateView

urlpatterns = [
    url(r'^me/(?P<pk>\d+)/$', ProfileDetailView.as_view(), name='my_profile'),
    url(r'^$', LoginView.as_view(), name="login"),
    url(r'^about/$', AboutView.as_view(), name='about'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^home/$', home, name='home'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^update_school/', SchoolAddressUpdateView.as_view(), name="update_school"),
    url(r'^update_village/', VillageUpdateView.as_view(), name="update_village"),
]