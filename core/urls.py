"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from gradebook.views import home_view, journal_view,admin_dashboard_view
from rest_framework.routers import DefaultRouter
from gradebook.api_views import ScheduleViewSet, GradeViewSet, HomeworkViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register(r"schedules", ScheduleViewSet, basename="api-schedules")
router.register(r"grades", GradeViewSet, basename="api-grades")
router.register(r"homeworks", HomeworkViewSet, basename="api-homeworks")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django.contrib.auth.urls")),
    path("", home_view, name="home"),
    path("journal/<slug:slug>/", journal_view, name="journal_detail"),
    path("admin-panel/", admin_dashboard_view, name="admin_dashboard"),
    path("api/v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
