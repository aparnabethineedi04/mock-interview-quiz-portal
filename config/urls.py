"""
URL configuration for quiz-portal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/', include('quizzes.api_urls')),
    # Landing page for project setup
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
