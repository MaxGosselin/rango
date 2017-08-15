# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    # CharField max length
    cf_max_len = 128
    name = models.CharField(max_length=cf_max_len, unique=True)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'


    def __str__(self):
        return self.name

class Page(models.Model):
    cf_max = 128
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=cf_max)
    url = models.URLField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    # Link our model to a User model instance.
    user = models.OneToOneField(User)

    # Additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the unicode methode to return something human
    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

