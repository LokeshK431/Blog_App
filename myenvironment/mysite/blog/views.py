import contextlib
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import timezone
from blog.models import Post,Comment
from blog.forms import PostForm, CommentForm
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin #Class based views

from django.contrib.auth.decorators import login_required #Function based views
from django.views.generic import(TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)

from . forms import PostForm

from django.contrib.auth import authenticate, login

from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse, HttpResponseRedirect

from blog.models import MyModel
import datetime

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponse('Registration successful!')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form':form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse('Login Successful!' )
        else:
            error_message = 'Invalid Email or Password'

            return render(request, 'registration/login.html', {'error_message':error_message})
    else:
        return render(request, 'registration/login.html')

def my_view(request):
    if request.method == 'POST':
        form = PostForm()
        if form.is_valid():
            return render(request, 'login.html', {'form':form})
        else:
            form = PostForm()

class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte = timezone.now()) .order_by('-published_date')
    
class PostDetailView(DetailView):
    model = Post

class CreatePostView(CreateView, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):
        some_date = datetime.date(2023, 3, 28)
        MyModel.objects.filter(create_date=some_date)
        return Post.objects.filter(published_date__isnull = True) .order_by('create_date')
    
#######################

@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit = False)
            comment.post = post
            comment.save()
            
            return HttpResponseRedirect('post_detail', pk=post.pk)
            
        else:
            form = CommentForm()
            return render(request,'blog/comment_form.html', {'form':form}, context_instance=RequestContext(contextlib))
        
@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail', pk = comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)