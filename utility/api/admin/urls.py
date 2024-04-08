from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
urlpatterns = [

    path("global-settings/", views.GlobalSettingsAPI.as_view())
]
urlpatterns += router.urls
