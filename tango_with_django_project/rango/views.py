# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    #dict for template engine
    #note: boldmessage is same as {{ boldmessage }} in the template
    context_dict = {'boldmessage': "Will you PLEASE clap? :("}

    #return a rendered response; first param is the template we want to use
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'aboutText': "Rango says I'm about this life.",
                    'authorText': "This tutorial compiled by Max Gosselin."
            }

    return render(request, 'rango/about.html', context=context_dict)
