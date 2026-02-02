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
    return render(request, "main/rekomendasi.html", {
        "page_name": "Rekomendasi",
        "page_title": "Rekomendasi"
    })

@login_required(login_url='login')
def riwayat_rekomendasi(request):
    return render(request, 'main/riwayat-rekomendasi.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def revise(request):
    return render(request, 'main/revise.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })

@login_required(login_url='login')
def detail(request):
    return render(request, 'main/detail-data.html',{
        "page_name": "Riwayat Rekomendasi",
        "page_title":"Riwayat Rekomendasi"
    })
