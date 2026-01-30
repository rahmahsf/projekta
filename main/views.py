from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'main/dashboard.html')

@login_required(login_url='login')
def rekomendasi(request):
    return render(request, 'main/rekomendasi.html')
