from __future__ import unicode_literals
#from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from django.utils import timezone
from community.models import Village, School
from django.utils.text import slugify
from django.db.models import Q


class PostManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())

    def post_for_user_village(self, user):
        return super(PostManager, self).filter(village=user.village).filter(posts_for_village=True)

    def post_for_user_school(self, user):
        return super(PostManager,
                     self).filter(school=user.school).filter(posts_for_school=True)

    def post_for_public(self):
        return super(PostManager,
                     self).filter(draft=False).filter(public=True).filter(publish__lte=timezone.now())


def upload_location(instance, filename):
    print(instance.id)
    return "posts/%s/%s" % (str(instance.id), filename)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    village = models.ForeignKey(Village)
    school = models.ForeignKey(School)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to=upload_location, null=True, blank=True, width_field="width_field", height_field="height_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    draft = models.BooleanField(default=False)
    public = models.BooleanField(default=True)
    posts_for_village = models.BooleanField(blank=False)
    posts_for_school = models.BooleanField(blank=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    objects = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:detail", kwargs={"slug": self.slug})

    class Meta:
        ordering = ["-timestamp", "-updated"]


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)
