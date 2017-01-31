from __future__ import unicode_literals
from django.db.models.signals import pre_save, post_save
from django.db import models
from people.models import Member
from community.models import StudentNeed
from django.conf import settings
import braintree

# used only in development stage - when DEBUG is set true in settings.
if settings.DEBUG:
    braintree.Configuration.configure(braintree.Environment.Sandbox,
                                      merchant_id=settings.BRAINTREE_MERCHANT_ID,
                                      public_key=settings.BRAINTREE_PUBLIC,
                                      private_key=settings.BRAINTREE_PRIVATE)


def get_sentinel_user():
    return Member.objects.get_or_create(username='deleted_user')[0]


class Support(models.Model):
    sponser = models.ForeignKey("support.Sponser", on_delete=models.PROTECT, blank=True, null=True)
    studentneed = models.ForeignKey(StudentNeed)

    def __unicode__(self):
        return str(self.sponser)+"<->"+str(self.studentneed)


class Sponser(models.Model):
    email = models.EmailField(unique=True)
    braintree_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.OneToOneField(Member, null=True, on_delete=models.PROTECT)

    def __unicode__(self):
        return self.email

    @property   
    def get_braintree_id(self):
        if not self.braintree_id:
            result = braintree.Customer.create({
                "email": self.email
                })
            if result.is_success:
                self.braintree_id = result.customer.id
                self.save()
        return self.braintree_id

    def get_client_token(self):
        customer_id = self.get_braintree_id
        if customer_id:
            client_token = braintree.ClientToken.generate({
                "customer_id": customer_id
                })
            return client_token
        return None


def update_braintree_id(sender, instance, *args, **kwargs):
    if not instance.braintree_id:
        instance.get_braintree_id


post_save.connect(update_braintree_id, sender=Sponser) 

SUPPORT_STATUS = (
        ('on process', 'On Process'),
        ('completed', 'Completed'),
)


class SupportDetail(models.Model):
    status = models.CharField(max_length=120, choices=SUPPORT_STATUS, default='on process')
    support = models.ForeignKey(Support, on_delete=models.PROTECT, blank=True, null=True)
    user = models.ForeignKey(Sponser, on_delete=models.PROTECT, blank=True, null=True)
    amount = models.DecimalField(max_digits=50, decimal_places=2)

    def __unicode__(self):
        return str(self.support)

    class Meta:
        ordering = ["-id"]

    def mark_completed(self):
        self.status = "completed"
        self.save()
