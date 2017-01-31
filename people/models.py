from __future__ import unicode_literals

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class Member(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    uid = models.CharField(max_length=255)
    access_token = models.TextField()
    village = models.ForeignKey("community.Village", models.SET_NULL, blank=True, null=True)
    school = models.ForeignKey("community.School", models.SET_NULL, blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_village_admin = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_profile(self):
        return self

    def get_village(self):
        return self.village

    def get_school(self):
        return self.school
