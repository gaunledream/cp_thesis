from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponse
from django.shortcuts import redirect


class AdminRequiredMixin(object):
    @classmethod
    def as_view(self, *args,**kwargs):
        view = super(AdminRequiredMixin, self).as_view(*args, **kwargs)
        return login_required(view) #to hide the admin site (can be done by changing the admin url)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_school_admin:
            return super(AdminRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("you are not school admin - check community/mixins and raise Http404 (not implemented yet)")


class LoginRequiredMixin(object):
    @classmethod
    def as_view(self, *args,**kwargs):
        view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
        return login_required(view)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
