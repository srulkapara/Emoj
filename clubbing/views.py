from django.shortcuts import render
from django.http import HttpResponse
import random
# Create your views here.


def get_initial_page(request):
    phrase = random.choice(["Yo Mama", "My Mama", "His Mama"])
    return HttpResponse(phrase)

