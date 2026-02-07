from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import os

def home(request):
    return HttpResponse("Chemical Equipment Visualizer Backend is Running! 🚀<br>Go to <a href='/admin/'>/admin/</a> or use <a href='/api/upload/'>/api/upload/</a>")

def serve_react(request):
    try:
        return render(request, 'index.html')
    except Exception as e:
        return HttpResponse(f"React Build Not Found. Please run 'npm run build' in web/ directory. Error: {e}", status=404)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("equipment.urls")),
    path("", serve_react), # Catch-all for React
    # re_path(r'^(?:.*)/?$', serve_react), # Optional: for client-side routing if we had it
]
