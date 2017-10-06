# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    # Get a list of all categories from the db.
    # Pass top 5 categories -- by likes -- to the context dict
    category_list = Category.objects.order_by('likes')[:5]

    # Get top 5 pages
    page_list = Page.objects.order_by('views')[:5]

    # Dict for template engine
    # Pass top 5 categories -- by likes -- to the context dict
    # Pass top 5 pages -- by likes -- to the context dict
    context_dict = {'categories': category_list,
                    'pages': page_list,
                    }

    # Cookie handling
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    # Build response; first param is the template we want to use
    response = render(request, 'rango/index.html', context=context_dict)

    # Return response back to the user, updating cokies that need to be changed
    return response

def about(request):
    # Check if cookie was accepted by the client.
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    visitor_cookie_handler(request)

    context_dict = {'visits': request.session['visits'],
                    'aboutText': "Rango says I'm about this life.",
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
        # Not a POST, render form
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form,
                'profile_form': profile_form,
                'registered': registered})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        # If we have a user obj, auth passed.
        if user:
            if user.is_active:
                # Valid, active user. Let's log them in.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # Inactive account.
                return HttpResponse("Your account is disabled.")
        else:
            # An inactive account was used - no loggin in!
            print(("Invalid login details" +\
                    ": {0}, {1}").format(username, password))
            return HttpResponse("Invalid login details supplied.")
    else:
        # No login attempted, render login form.
        return render(request, 'rango/login.html', {})


@login_required
def user_logout(request):
    # Logout
    logout(request)
    # Back to index
    return HttpResponseRedirect(reverse('index'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Cookie helper
    # Get number of visits to the site

    visits = get_server_side_cookie(request, 'visits', '1')

    last_visit_cookie = get_server_side_cookie(request,
            'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
            '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    elif visits:
        pass
    else:
        visits = 1
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits


