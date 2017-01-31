from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
from django.contrib import messages
from django.core.mail import send_mass_mail, send_mail
import braintree
from .models import Sponser, SupportDetail, Support
from community.models import StudentNeed
from .forms import GuestDonationForm
from django.conf import settings

braintree.Configuration.configure(braintree.Environment.Sandbox,
    merchant_id=settings.BRAINTREE_MERCHANT_ID,
    public_key=settings.BRAINTREE_PUBLIC,
    private_key=settings.BRAINTREE_PRIVATE)


class SupportOrderView(FormMixin, DetailView):
    model = SupportDetail
    template_name = "support/support_procedure.html"
    form_class = GuestDonationForm

    def get_object(self, *args, **kwargs):
        users = SupportDetail.objects.all()
        user_list = list(users[:1])
        if user_list:
            return user_list[0]
        return None

    def get_context_data(self, *args, **kwargs):
        context = super(SupportOrderView, self).get_context_data(*args, **kwargs)
        user_can_continue = False
        sponser_id = self.request.session.get("sponser_id")
        self.request.session["pk_need"] = self.kwargs["pk"]
        if self.request.user.is_authenticated():
            user_can_continue = True
            sponser, created = Sponser.objects.get_or_create(email=self.request.user.email)
            sponser.user = self.request.user
            sponser.save()
            context["client_token"] = sponser.get_client_token()
            self.request.session["sponser_id"] = sponser.id

        if sponser_id is not None:
            user_can_continue = True
            if not self.request.user.is_authenticated():
                sponser_2 = Sponser.objects.get(id=sponser_id)
                context["client_token"] = sponser_2.get_client_token()
        context["user_can_continue"] = user_can_continue
        context["form"] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data.get("email")
            sponser, created = Sponser.objects.get_or_create(email=email)
            if created:
                sponser.email = email
                sponser.save()
            request.session["sponser_id"] = sponser.id
            request.session["guest_sponser_email"] = sponser.email
            request.session['pk_need'] = self.kwargs["pk"]
            supporter_exists = Sponser.objects.filter(email=email).count()
            if supporter_exists != 0:
                messages.success(request, "Would you like to be member to make record of your frequent supports?")
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('sponser', kwargs={'pk': self.request.session['pk_need']})

    def get(self, request, *args, **kwargs):
        get_data = super(SupportOrderView, self).get(request, *args, **kwargs)
        return get_data


class SupportFinalCheckoutView(View):
    def post(self, request, *args, **kwargs):
        donation_total = request.POST.get("donation-amount")
        if Decimal(donation_total) < 1:
            messages.success(request, "Please, at least a dollar before you request for sponsering!")
            return HttpResponseRedirect(reverse('sponser', kwargs={'pk': self.request.session['pk_need']}))
        nonce = request.POST.get("payment_method_nonce")
        if nonce:
            result = braintree.Transaction.sale({
                "amount": donation_total,
                "payment_method_nonce": nonce,
                "options": {
                    "submit_for_settlement": True
                }
            })
        if result.is_success:
            if self.request.user.is_authenticated():
                email = self.request.user.email
            else:
                email = self.request.session["guest_sponser_email"]
            sponser, created_sponser = Sponser.objects.get_or_create(email=email)
            studentneed=StudentNeed.objects.get(pk=self.request.session['pk_need'])
            support, created_support = Support.objects.get_or_create(sponser=sponser, studentneed=studentneed)
            support_detail_count = SupportDetail.objects.filter(user=sponser, support=support).count()
            # if it is financial requirements
            if studentneed.need.id == 2:
                new_support_detail = SupportDetail(user=sponser, support=support, amount = donation_total)
                new_support_detail.save()
                studentneed.achievement = Decimal(studentneed.achievement) + Decimal(donation_total)
                if studentneed.achievement >= studentneed.target:
                    studentneed.completed = True
                    studentneed.active = False
                    mass_emails = []
                    for each_sponser in studentneed.sponsers.all():
                        mass_emails.append((
                            "Thank you for beleiving our cause in CPNepal",
                            "Dear "+ each_sponser.email+"!\nWe are glad to announce that your support has enabled us to achieve the needs of our student: "+ str(studentneed.student)+". We thank you! \nGood works will definitely spread!",
                            settings.ADMINS,
                            [each_sponser.email],
                            ))
                        try:
                            send_mass_mail(mass_emails)
                            messages.success(request, 'Please, we sent you thank you message!')
                        except:
                            messages.error(request, "Thank You email delivery failutre notification!")
            else:#if this payment is for something else
                if support_detail_count < 1:
                    new_support_detail = SupportDetail(user=sponser, support=support, amount = donation_total)
                    new_support_detail.save()
                    studentneed.achievement = Decimal(studentneed.achievement) + 1
                    if studentneed.achievement >= studentneed.target:
                        studentneed.active = False
                    #both sender and receiver ADMIN for hiding this info in github
                    send_mail("One sponsers interested!", "Hello Admin!\n"+sponser.email+" is interested to support "+ str(studentneed) +". Please, check and confirm the sponsership! You need to update the support details table after confirming the sponsership!",settings.ADMINS, [settings.ADMINS],)
                else:
                    get_support_detail = SupportDetail.objects.get(user=sponser, support=support)
                    print get_support_detail
                    get_support_detail.amount = Decimal(get_support_detail.amount) + Decimal(donation_total)
                    get_support_detail.save()

            studentneed.save()
            messages.success(request, "Thank you for your support. Have a nice day!")
            del request.session["pk_need"]#add session to be deleted here!
        else:
            messages.success(request, "%s" %(result.message))
            return HttpResponseRedirect(reverse('sponser', kwargs={'pk': self.request.session['pk_need']}))
        return redirect("posts:list")
                
    def get(self, request, *args, **kwargs):
        print request.POST.get("payment_token")
        return redirect("home")
