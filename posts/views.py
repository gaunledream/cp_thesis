from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib import quote_plus
"""Post apps are basically my starting to learn Django framework and codes are used from
the tutorial in Udemy (Coding for Entrepreneurs)"""


@login_required(login_url="/")
def posts_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.village = request.user.village
        instance.school = request.user.school
        instance.save()
        messages.success(request, "Post created successfully!")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)


def posts_detail(request, slug=None):
    try:
        instance_post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        raise Http404("No Post matches the given query. Would you rather like to visit home page?")
    if not request.user.is_authenticated():
        if not instance_post.public:
            raise Http404("Only public posts for anonymous user")
    else:
        if not (instance_post.public or instance_post.village == request.user.village or instance_post.school == request.user.school):
            raise Http404("Not here as the post does not belong to your criterion even you are logged in!")
    context = {
        "title": instance_post.title,
        "instance": instance_post,
    }
    return render(request, "post_detail.html", context)


def posts_list(request): #list
    try:
        queryset_list = Post.objects.post_for_public().order_by("-timestamp")
        query = request.GET.get('query')
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__name__icontains=query)
                    ).distinct()
        page_request_var = "no-page"
        paginator = Paginator(queryset_list, 3)  # Show 25 contacts per page
        page = request.GET.get(page_request_var)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            queryset = paginator.page(paginator.num_pages)

        context = {
            "object_list":queryset,
            "title":"List",
            "page_request_var": page_request_var,
        }
        return render(request,"post_list.html", context)
    except Post.DoesNotExist:
        if request.user.is_authenticated():
            messages.warning(request, "No posts, so redirected to home!")
            return redirect('posts:create')
    except:
        pass


@login_required(login_url="/")
def posts_update(request, slug=None):#edit
    try:
        instance_post = Post.objects.get(slug=slug)
    except Post.DoesNotExist:
        raise Http404("No Post matches the given query. Would you rather like to visit home page?")
    if not request.user ==  instance_post.user:
        raise Http404("Wrong user!")
    form = PostForm(request.POST or None, request.FILES or None, instance=instance_post)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Successfully updated")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "title": instance_post.title,
        "instance_post": instance_post,
        "form": form
    }
    return render(request, "post_form.html", context)


@login_required(login_url="/")
def posts_delete(request, slug=None):#delete item
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404("You need to be staff!")
    instance_post = get_object_or_404(Post, slug=slug)
    instance_post.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")


@login_required(login_url="/")
def posts_school_list(request):
    try:
        queryset_list = Post.objects.post_for_user_school(request.user).order_by("-timestamp")
        query = request.GET.get('query')
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query)|
                    Q(user__last_name__icontains=query)
                    ).distinct()
        page_request_var = "no-page"
        paginator = Paginator(queryset_list, 3)  # Show 3 posts
        page = request.GET.get(page_request_var)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger: # If page no int, then first page
            queryset=paginator.page(1)
        except EmptyPage: #for out of range, last page
            queryset = paginator.page(paginator.num_pages)
        context = {
                "object_list":queryset,
                "title":"List",
                "page_request_var":page_request_var,
                }
        return render(request,"post_list.html", context)
    except Post.DoesNotExist:
        if request.user.is_authenticated():
            messages.warning(request, "You don't have school posts, would you like to create?")
            return redirect('posts:create')
    except:
        pass


@login_required(login_url="/")
def posts_village_list(request):
    try:
        queryset_list = Post.objects.post_for_user_village(request.user).order_by("-timestamp")
        query = request.GET.get('query')
        if query:
            queryset_list = queryset_list.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(user__first_name__icontains=query)|
                    Q(user__last_name__icontains=query)
                    ).distinct()
        page_request_var = "no-page"
        paginator = Paginator(queryset_list, 3)  # Show 3 posts
        page = request.GET.get(page_request_var)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger: # If page no int, then first page
            queryset=paginator.page(1)
        except EmptyPage: #for out of range, last page
            queryset = paginator.page(paginator.num_pages)
        context = {
                "object_list":queryset,
                "title":"List",
                "page_request_var":page_request_var,
                }
        return render(request,"post_list.html", context)
    except Post.DoesNotExist:
        messages.warning(request, "You don't have village posts, would you like to create?")
        if request.user.is_authenticated():
            return redirect('posts:create')
    except:
        pass
