# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):


    # Get a list of all categories from the db.
    # Pass top 5 categories -- by likes -- to the context dict
    category_list = Category.objects.order_by('likes')[:5]

    # Get top 5 pages
    page_list = Page.objects.order_by('views')[:5]

    #dict for template engine
    # Pass top 5 categories -- by likes -- to the context dict
    # Pass top 5 pages -- by likes -- to the context dict
    context_dict = {'categories': category_list,
                    'pages': page_list,
                    }

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

def add_category(request):
    form = CategoryForm()

    # HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Valid form?
        if form.is_valid():
            # Save to database
            form.save(commit=True)

            # We can go anywhere from here, a confirmation msg, or to some other page.
            # Since the newest categories are shown at the index page, we'll go there.
            return index(request)
        else:
            # Form was invalid, print errors to terminal.
            print(form.errors)

    # Get to here: form isnt valid and complete
    # This return will handle all cases: bad form, new form, missing cases.
    # Render the form with error messages too (if any).
    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()

    # POST?
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # Save to db
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            # Back to category list.
            return show_category(request, category_name_slug)
        else:
            print(form.errors)
    # Render form again with error messages.
    context_dict = {'form': form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    # True if registration is successful.
    registered = False

    # If POST then we want to process form data
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save user data to db
            user = user_form.save()

            # Hash pw and update obj
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            # Invalid form or forms. Print errors to term.
            print(user_form.errors, profile_form.errors)
    else:
        # Not a POST, renderforms
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered})

