from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

# Create your views here.


def profile(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')

def deshboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'dashboard.html')

def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'about.html')