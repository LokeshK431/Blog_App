from django.db import models
from django.utils import timezone
from django.urls import reverse
from django import template

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django import forms

import re

import datetime

class MyModel(models.Model):
    create_date = models.DateField(default=datetime.date.today)

    def get_queryset(self):
        some_date = datetime.date(2023, 3, 29)
        MyModel.objects.filter(create_date = some_date)
        return Post.objects.filter(published_date__isnull = True) .order_by('create_date')

class MyUserManager(BaseUserManager):
    def create_user(self, email, password = None):
        if not email:
            raise ValueError('Email ID mandatory!')
        
        user = self.model(
            email = self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
class MyForms(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('Password must have a mix of 8 characters')
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must have one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Password must have one lowercase letter')
        
        if not re.search(r'[!@#$%^&*()_+{}[\]:;.,<>?]', password):
            raise forms.ValidationError('Password must have one special character(!@#$%^&*()_+{}[\]:;.,<>?)')

        if not any(c.isuper() for c in password):
            raise forms.ValidationError('Password must contain atleast one uppercase letter')
        
        return password
    
    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_admin = True
        user.save(using = self._db)
        return user
    
    class MyUser(AbstractBaseUser):
        email = models.EmailField(
            verbose_name='email address',
            max_length=300,
            unique = True,
        )

        is_active = models.BooleanField(default=True)
        is_admin = models.BooleanField(default=False)

        objects = MyUserManager()

        USERNAME_FIELD = 'email'

        def __str__(self):
            return self.email
        
        def has_perm(self, perm, obj=None):
            return True
        
        def has_module_perms(self, app_label):
            return True
        
        @property
        def is_staff(self):
            return self.is_admin

register = template.Library()
@register.simple_tag
def static():
    return static

@register.filter(name='parse_remainder')
def parse_remainder(value):
    return value.split('=')[0]


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now())
    published_date = models.DateTimeField(blank=True,null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def approve_comments(self):
        return self.comments.filter(approved_comment=True)
    
    def get_absolute_url(self):
        return reverse("post_detail", kwargs = {'pk':self.pk})
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    text = models.TextField()
    create_date = models.DateTimeField(default=timezone.now())
    approved_comment = models.BooleanField(default=False)
    create_time = models.DateTimeField(default=timezone.now())

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text