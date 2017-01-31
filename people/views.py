import random
from datetime import datetime, timedelta

from community.mixins import LoginRequiredMixin
from community.models import StudentNeed, School, Village
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .forms import VillageAddForm, SchoolAddFormSet
from .models import Member


# Create your views here.


#####################################################################
#####################################################################
class LoginView(View):
    def get(self, request):
        one_year = datetime.today() - timedelta(days=365)
        needs = (sorted(StudentNeed.objects.filter(published_date__gte=one_year, active=True, student__is_public=True).order_by("-last_updated", "-published_date")[:30], key = lambda x: random.random()))[:4]
        if request.GET.get('next'):
            next=request.GET['next']
            context = {"needs": needs, "next":next}
        else:
            context = {"needs":needs}
        return render(request, 'login.html', context)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Member

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        return context

    def get_object(self):
            obj = get_object_or_404(self.model, pk=self.kwargs['pk'])
            user = self.request.user
            if not obj == user:
                raise PermissionDenied
            return obj

    def dispatch(self, request, *args, **kwargs):
            try:
                return super(ProfileDetailView, self).dispatch(request, *args, **kwargs)
            except PermissionDenied:
                messages.error(request, "You can only view your own profile!")
                return redirect('my_profile', pk=self.request.user.id)


# for contact, about us, and home and logout  - some views are implemented using function instead of CBV
def contact(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('subject', ''):
            errors.append('Enter a subject.')
        if not request.POST.get('message', ''):
            errors.append('Enter a message.')
        if not request.POST.get('email', ''):
            errors.append('Enter an email.')
        if not request.POST.get('email') and '@' not in request.POST['email']:
            errors.append('Enter a valid e-mail address.')
        if not errors:
            try:
                send_mail(request.POST['subject'], request.POST['message'], request.POST.get('email'), [settings.ADMINS],)
                messages.success(request, 'Thank you for your email!')
                return render(request, 'contact.html')
            except Exception, err: 
                return HttpResponse(str(err))
    return render(request, 'contact.html', {'errors': errors})


class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')


def home(request):
    return redirect('people:login')#name for login view set in url.py


def logout(request):
    auth_logout(request)
    return redirect('people:login')


class VillageUpdateView(LoginRequiredMixin, UpdateView):
    model = Village
    form_class = VillageAddForm
    success_url="/update_school"
    template_name="people/set_village.html"

    def get_context_data(self, *args, **kwargs):
        context = super(VillageUpdateView, self).get_context_data(*args, **kwargs)
        context['list_village'] = Village.objects.exclude(name__icontains="default")
        return context
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank version of the form
        and its inline formsets.
        """
        created_by_this_user = Village.objects.filter(Q(created_by=self.request.user) & ~Q(name = "default"+str(self.request.user))).count()
        if self.request.user.village and self.request.user.village.is_verified:
            messages.success(self.request, "You already have your village set in your profile. Contact us!")
            return  redirect("home")
        if created_by_this_user >= 2:#can create two village -one is hometown, another is where  the school is!
            messages.success(self.request, "You can create only 2 villages if it does not exist! You can contact us!")
            return  redirect("home")
        else:
            self.object = self.get_object()
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and them checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            village = form.save(commit=False)
            village.created_by = self.request.user
            village.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self):
        return self.request.user.village

    def form_invalid(self, form):
        #do find this village only if you get error that says that the village already exists: village = Village.objects.get(name=form.data.get("name"), district=form.data.get("district"))#now work from here!
        #print village
        find_message = "Village with this Name and District already exists"
        errors = str(form.errors)
        if find_message in errors:
            village = Village.objects.get(name=form.data.get('name'),
                    district=form.data.get('district'))
            if not village.is_verified and not (village.created_by == self.request.user):
                village.is_verified = True
                village.save()
            self.request.user.village = village
            self.request.user.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


#####################################################################
#####################################################################


class SchoolAddressUpdateView(LoginRequiredMixin, UpdateView):
    """Used to change the address of the school - the users have limited choice for doing changes"""
    template_name = "people/set_school.html"
    model = Village
    form_class = VillageAddForm
    success_url = "/"

    def get_context_data(self, *args, **kwargs):
        context = super(SchoolAddressUpdateView, self).get_context_data(*args, **kwargs)
        context['list_school'] = School.objects.exclude(name__icontains="default")
        return context

    def get_object(self):
        return self.request.user.school.village

    def get(self, request, *args, **kwargs):#blank version of form
        self.object = self.get_object()
        schools = School.objects.filter(name=self.request.user.school.name)
        created_by_this_user = School.objects.filter(Q(created_by=self.request.user) & ~Q(name = "default"+str(self.request.user)) & ~Q(village=None)).count()
        if created_by_this_user >= 1:    
            messages.success(self.request, "You can create only 1 school if it does not exist! You can contact us!")
            return redirect("home")
        if self.request.user.school and self.request.user.school.is_verified:
            messages.success(self.request, "You already have your school set in your profile. Contact us for changes!")
            return redirect("home")
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            school_form = SchoolAddFormSet(initial=[(self.request.user.school).__dict__])
            return self.render_to_response(
                self.get_context_data(form=form,
                                  school_form=school_form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        created_by_this_user = School.objects.filter(Q(created_by=self.request.user) & ~Q(name = "default"+str(self.request.user)) &~Q(village=None)).count()
        if created_by_this_user >= 1:#can create two village -one is hometown, another is where  the school is!
            messages.success(self.request, "You can create only 1 school if it does not exist! You can contact us!")
            return redirect("home")
        if self.request.user.school and self.request.user.school.is_verified:
            messages.success(self.request, "You already have your school set in your profile. Contact us for changes!")
            return redirect("home")
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            school_form = SchoolAddFormSet(self.request.POST)
            #print school_form
            if form.is_valid() and school_form.is_valid():
                return self.form_valid(form, school_form)
            else:
                return self.form_invalid(form, school_form)

    def form_valid(self, form, school_form):
        form.instance.created_by = self.request.user#this is village
        village = form.save(commit=False)
        village.save()
        #school_form.instance.created_by = self.request.user
        school_form.instance = village
        school = school_form.save(commit=False)#returns list of school from inlineformset
        first_school = school[0]
        first_school.created_by = self.request.user
        try:#this is needed to check, because update form does not send error when school and village are set same in post form
            school_exists = School.objects.get(name__iexact=first_school.name, village=school_form.instance)
        except School.DoesNotExist:
            school_exists = None
        if school_exists:
            first_school = school_exists
        #school.save()
        first_school.save()
        self.request.user.school=first_school
        School.objects.filter(created_by=self.request.user, village=None).delete()
        self.request.user.save()
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form, school_form):
        find_message = "Village with this Name and District already exists"
        errors = str(form.errors)
        if find_message in errors and school_form.is_valid():
            village = Village.objects.get(name=form.data.get('name'),
                    district=form.data.get('district'))
            if not village.is_verified and not (village.created_by == self.request.user):
                village.is_verified = True
                village.save()
            self.request.user.school.village = village
            self.request.user.save()
            for form_data in school_form:
                clean_data = form_data.cleaned_data
                name_school = clean_data.get('name')
                description = clean_data.get('description')
            form_school, created_by_this_user = School.objects.get_or_create(name=name_school, village=village)
            if created_by_this_user:
                form_school.created_by = self.request.user
                form_school.description = description
            else:
                if not form_school.is_verified and not (form_school.created_by == self.request.user):
                    form_school.is_verified = True
            form_school.save()
            self.request.user.school = form_school
            self.request.user.save()
            School.objects.filter(created_by=self.request.user, village=None).delete()
            return redirect(self.success_url)
        return self.render_to_response(
            self.get_context_data(form=form,
                                  school_form=school_form))


