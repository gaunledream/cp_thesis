from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models
from django.core.urlresolvers import reverse
from people.models import Member


class StudentNeedManager(models.Manager):
    def get_related(self, instance, user):
            if user.is_authenticated():
                student_with_same_need = self.get_queryset().filter(active=True, need=instance.need)
            else:
                student_with_same_need = self.get_queryset().\
                    filter(active=True, need=instance.need, student__is_public=True)
            student_from_same_village=self.get_queryset().\
                filter(active=True, student__village=instance.student.village)
            student_from_same_school=self.get_queryset().filter(active=True, student__school=instance.student.school)
            #returns 4 distinct students with same need
            return (student_with_same_need |
                    student_from_same_village | student_from_same_school).exclude(id=instance.id).distinct()[:4]

DISTRICT_NEPAL = (
        ('jhapa', 'Jhapa District'),
        ('ilam', 'Ilam District'),
        ('panchthar', 'Panchthar District'),
        ('taplejung', 'Taplejung District'),
        ('morang', 'Morang District'),
        ('sunsari', 'Sunsari District'),
        ('bhojpur', 'Bhojpur District'),
        ('dhankuta', 'Dhankuta District'),
        ('terhathum', 'Terhathum District'),
        ('sankhuwasabha', 'Sankhuwasabha District'),
        ('saptari', 'Saptari District'),
        ('siraha', 'Siraha District'),
        ('udayapur', 'Udayapur District'),
        ('khotang', 'Khotang District'),
        ('okhaldhunga', 'Okhaldhunga District'),
        ('solukhumbu', 'Solukhumbu District'),
        ('dhanusa', 'Dhanusa District'),
        ('mahottari', 'Mahottari District'),
        ('sarlahi', 'Sarlahi District'),
        ('sindhuli', 'Sindhuli District'),
        ('ramechhap', 'Ramechhap District'),
        ('dolakha', 'Dolakha District'),
        ('bhaktapur', 'Bhaktapur District'),
        ('dhading', 'Dhading District'),
        ('kathmandu', 'Kathmandu District'),
        ('kavrepalanchok', 'Kavrepalanchok District'),
        ('lalitpur', 'Lalitpur District'),
        ('nuwakot', 'Nuwakot District'),
        ('rasuwa', 'Rasuwa District'),
        ('sindhupalchok', 'Sindhupalchok District'),
        ('bara', 'Bara District'),
        ('parsa', 'Parsa District'),
        ('rautahat', 'Rautahat District'),
        ('chitwan', 'Chitwan District'),
        ('makwanpur', 'Makwanpur District'),
        ('gorkha', 'Gorkha District'),
        ('kaski', 'Kaski District'),
        ('lamjung', 'Lamjung District'),
        ('syangja', 'Syangja District'),
        ('tanahun', 'Tanahun District'),
        ('manang', 'Manang District'),
        ('kapilvastu', 'Kapilvastu District'),
        ('nawalparasi', 'Nawalparasi District'),
        ('rupandehi', 'Rupandehi District'),
        ('arghakhanchi', 'Arghakhanchi District'),
        ('gulmi', 'Gulmi District'),
        ('palpa', 'Palpa District'),
        ('baglung', 'Baglung District'),
        ('myagdi', 'Myagdi District'),
        ('parbat', 'Parbat District'),
        ('mustang', 'Mustang District'),
        ('dang', 'Dang Deukhuri District'),
        ('pyuthan', 'Pyuthan District'),
        ('rolpa', 'Rolpa District'),
        ('rukum', 'Rukum District'),
        ('salyan', 'Salyan District'),
        ('dolpa', 'Dolpa District'),
        ('humla', 'Humla District'),
        ('jumla', 'Jumla District'),
        ('kalikot', 'Kalikot District'),
        ('mugu', 'Mugu District'),
        ('banke', 'Banke District'),
        ('bardiya', 'Bardiya District'),
        ('surkhet', 'Surkhet District'),
        ('dailekh', 'Dailekh District'),
        ('jajarkot', 'Jajarkot District'),
        ('kailali', 'Kailali District'),
        ('achham', 'Achham District'),
        ('doti', 'Doti District'),
        ('bajhang', 'Bajhang District'),
        ('bajura', 'Bajura District'),
        ('kanchanpur', 'Kanchanpur District'),
        ('dadeldhura', 'Dadeldhura District'),
        ('baitadi', 'Baitadi District'),
        ('darchula', 'Darchula District'),
)


def get_sentinel_user():
    return Member.objects.get_or_create(username='deleted_user')[0]


class Village(models.Model):
    name = models.CharField(max_length=50, blank=False)
    created_by = models.ForeignKey(Member, related_name="village_creator", default=1, on_delete=models.SET(get_sentinel_user))
    is_verified = models.BooleanField(default=False)
    district = models.CharField(max_length=15, choices=DISTRICT_NEPAL, default='taplejung')
    description = models.TextField()

    def __unicode__(self):
        return self.name + " in "+self.district

    class Meta:
        unique_together = ('name', 'district',)


class School(models.Model):
    name = models.CharField(max_length=120, blank=False)
    created_by = models.ForeignKey(Member, related_name="school_creator", default=1, on_delete=models.SET(get_sentinel_user))
    description = models.TextField()
    is_verified = models.BooleanField(default=False)
    village = models.ForeignKey(Village, on_delete=models.PROTECT, blank=True, null=True)
    class Meta:
        unique_together = ('name', 'village',)

    def __unicode__(self):
        return self.name + "<->" + str(self.village)


class Student(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    display_name = models.CharField(max_length=25, unique=True)
    grade = models.PositiveIntegerField()
    school = models.ForeignKey(School, on_delete=models.PROTECT, blank=True, null=True)
    village = models.ForeignKey(Village, on_delete=models.PROTECT, blank=True, null=True)
    requirements = models.ManyToManyField("Requirement", through="StudentNeed", blank=True)
    published_date = models.DateField(auto_now=False, auto_now_add=True)
    last_updated = models.DateField(auto_now=True, auto_now_add=False)
    show_full_name = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    description = models.TextField()

    def __unicode__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse("student_detail", kwargs={"pk": self.pk})

    def get_image_url(self):
        img = self.studentimage_set.first()
        if img:
            return img.image.url
        else:
            img #NONE


def image_upload_to(instance, filename):
    title = instance.student.display_name
    slug = slugify(title)
    return "students/%s/%s" %(slug, filename)


class StudentImage(models.Model):
    student = models.ForeignKey("Student")
    image = models.ImageField(upload_to=image_upload_to)

    def __unicode__(self):
        return self.student.display_name

    def get_absolute_url(self):
        return self.student.get_absolute_url()


class Requirement(models.Model):
    title = models.CharField(max_length=25, blank=False)
    description = models.TextField()

    def __unicode__(self):
        return self.title


class StudentNeed(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    sponsers = models.ManyToManyField("support.Sponser", through="support.Support")
    need = models.ForeignKey(Requirement, on_delete=models.PROTECT)
    target = models.PositiveIntegerField()
    achievement = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)#this field will remain not completed even if there are enough sponsers interested, but not finalized. active field will be disabled when enough sponsers
    active = models.BooleanField(default=True)
    measurement = models.CharField(max_length=10) #to specify how target is measured, for exmple, target is 1000 and measure is Nrs
    description = models.TextField()#student specific need description/story - seems this needs target
    published_date = models.DateField(auto_now=False, auto_now_add=True)
    last_updated = models.DateField(auto_now=True, auto_now_add=False)
    objects = StudentNeedManager()

    def __unicode__(self):
        return str(self.student.display_name) +" needs "+ str(self.need.title)

    def get_absolute_url(self):
        return reverse("studentneed_detail", kwargs={"pk": self.pk})
