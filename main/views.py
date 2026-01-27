from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate

# Create your views here.
def dashboard(request):
    return render(request, 'main/dashboard.html')