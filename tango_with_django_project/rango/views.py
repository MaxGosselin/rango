# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category, Page

def index(request):


    # Get a list of all categories from the db.
    # Pass top 5 -- by likes -- to the context dict
    category_list = Category.objects.order_by('likes')[:5]

    #dict for template engine
    context_dict = {'categories': category_list}

    #return a rendered response; first param is the template we want to use
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'aboutText': "Rango says I'm about this life.",
                    'authorText': "This tutorial compiled by Max Gosselin."
            }

    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dict
    context_dict = {}

    try:
        # Raises DoesNotExist except on fail.
        category = Category.objects.get(slug=category_name_slug)

        # Get all assosciated pages.
        pages = Page.objects.filter(category=category)

        # Add pages to c_d
        context_dict['pages'] = pages

        # Also pass the category
        context_dict['category'] = category
    except Category.DoesNotExist:

        context_dict['pages'] = None
        context_dict['category'] = None

    return render(request, 'rango/category.html', context_dict)


