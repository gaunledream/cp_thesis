# Create your views here.

from django.forms.models import modelformset_factory
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from datetime import datetime, timedelta
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.db.models import Q
import random

from .forms import StudentForm,  create_model_form, StudentImageForm
from .mixins import AdminRequiredMixin, LoginRequiredMixin
from .models import StudentNeed, Student, StudentImage


class StudentCreateView(AdminRequiredMixin, CreateView):
    """Creates student and the creator should have admin privilege as defined in AdminRequiredMixin -
    the admin belongs to the same school to the student created!"""
    model = Student
    form_class = StudentForm

    def form_valid(self, form):
        student = form.save(commit=False)
        student.school = self.request.user.school
        student.save()
        return super(StudentCreateView, self).form_valid(form)


class StudentImageCreateView(AdminRequiredMixin, CreateView):
    """Admin from the same school can change the image of the student from his school -
    otherwise redirects to student list page"""
    model = StudentImage
    form_class = StudentImageForm

    def form_valid(self, form):
        student_img = form.save(commit=False)
        student_img.student=Student.objects.get(pk=self.kwargs.get('pk'))
        if self.request.user.school != student_img.student.school:
            messages.error(self.request,"You are not allowed to add image to student from other school!")
            return redirect("student_list")
        student_img.save()
        return super(StudentImageCreateView, self).form_valid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    """
    Student Update - admin required for this action from the same school the student belongs to!
    """
    model = Student
    form_class = StudentForm

    def form_valid(self, form):
        student_mod = form.save(commit=False)
        if self.request.user.school != student_mod.school:
            messages.error(self.request, "You are not allowed to modify students from other school!")
            return redirect("student_list")
        student_mod.save()
        return super(StudentUpdateView, self).form_valid(form)


class StudentDeleteView(AdminRequiredMixin, DeleteView):
    """Deletes the students"""
    model = Student
    template_name="community/student_confirm_delete.html"
    success_url = reverse_lazy('student_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.school == self.object.school:
            return super(StudentDeleteView, self).delete(request, *args, **kwargs)
        else:
            messages.error(self.request, "You are not allowed to delete students from other school!")
            return redirect("student_list")


class StudentNeedListView(AdminRequiredMixin, ListView):
    login_url= "login"
    model = StudentNeed
    template_name = "community/studentneed_list.html"
    
    def get_queryset(self, *args, **kwargs):
        queryset = super(StudentNeedListView, self).get_queryset(*args, **kwargs)
        user = self.request.user
        student_pk=self.kwargs.get('pk')
        if student_pk:
            return queryset.filter(student=Student.objects.get(pk=student_pk), active=True)
        else:
            return queryset.filter(student__school = user.school, active=True)
    
    def get_context_data(self, *args, **kwargs):
        studentneedform = create_model_form(self.request.user)
        studentneedformset = modelformset_factory(StudentNeed, form=studentneedform, extra=1)
        context = super(StudentNeedListView, self).get_context_data(*args, **kwargs)
        context['formset'] = studentneedformset(queryset=self.get_queryset())
        return context
    
    def post(self, request, *args, **kwargs):
        studentneedform = create_model_form(self.request.user)
        studentneedformset = modelformset_factory(StudentNeed, form=studentneedform, extra=1)
        formset = studentneedformset(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                new_need = form.save(commit=False)
                if self.request.user.school != new_need.student.school:
                    messages.error(request, "You can only update student from own school!")
                    return redirect("studentneed_list")
                new_need.save()
            messages.success(request, "Your student needs are updated!")
            return redirect("studentneed_list")
        messages.error(request, "Student need update failure!")
        return redirect("studentneed_list")


class StudentListView(ListView):
    model = Student
    queryset = Student.objects.all()
    paginate_by="2"
    template = "community/student_list.html"

    def get_queryset(self, *args, **kwargs):
        queryset_list = super(StudentListView,
                        self).get_queryset(*args,
                                **kwargs).order_by("-published_date").filter(is_public=True)
        query = self.request.GET.get('query')
        if query:
            queryset_list = queryset_list.filter(Q(display_name__icontains=query) | Q(school__name__icontains=query) | Q(village__name__icontains=query)).distinct()
        return queryset_list

    def get_context_data(self, *args, **kwargs):
        context = super(StudentListView, self).get_context_data(*args, **kwargs)
        return context


class LocalStudentListView(LoginRequiredMixin, ListView):
    model = Student
    queryset = Student.objects.all()
    paginate_by="2"
    template = "community/student_list.html"

    def get_queryset(self, *args, **kwargs):
        queryset_list = super(LocalStudentListView, self).get_queryset(*args, **kwargs).order_by("-published_date")
        query = self.request.GET.get('query')
        user = self.request.user
        if user.is_authenticated():
            queryset_list = queryset_list.filter(Q(village=user.village)|Q(school=user.school)).distinct()
        if query:
            queryset_list = queryset_list.filter(Q(display_name__icontains=query) | Q(school__name__icontains=query) | Q(village__name__icontains=query)).distinct()
        return queryset_list

    def get_context_data(self, *args, **kwargs):
        context = super(LocalStudentListView, self).get_context_data(*args, **kwargs)
        one_year = datetime.today() - timedelta(days=365)
        needs = (sorted(StudentNeed.objects.filter(Q(published_date__gte=one_year)
                                                   & Q(active=True) & (Q(student__school=self.request.user.school)|
                                                                       Q(student__village=self.request.user.village))).
                        order_by("-last_updated", "-published_date")[:30], key = lambda x: random.random()))[:4]
        context['needs'] = needs
        return context


class StudentDetailView(DetailView):
    """get_object fetches the detail student, but raise PermissionDenied if student from different school or not public; and then
    that exception is caught during dispatch of the view"""
    model = Student
    def get_context_data(self, *args, **kwargs):
        context = super(StudentDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        need_set = obj.studentneed_set.all()
        context['need_set'] = need_set
        return context

    def get_object(self):
        obj = get_object_or_404(self.model, pk=self.kwargs['pk'])
        user = self.request.user
        if not obj.is_public:
            if user.is_authenticated() and (user.village == obj.village or user.school == obj.school):
                return obj
            else:
                raise PermissionDenied
        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(StudentDetailView, self).dispatch(request, *args, **kwargs)
        except PermissionDenied:
            messages.error(request, "Not available for this user!")
            return redirect('student_list')


class StudentNeedDetailView(DetailView):
    model = StudentNeed

    def get_context_data(self, *args, **kwargs):
        user = self.request.user
        #print StudentNeed.objects.get_related(self.get_object(), user)
        try:
            related_needs = sorted(StudentNeed.objects.get_related(self.get_object(), user)[:3], key=lambda x: random.random())
        except:
            related_needs = None
        context = super(StudentNeedDetailView, self).get_context_data(*args, **kwargs)
        context["related_needs"] = related_needs
        return context