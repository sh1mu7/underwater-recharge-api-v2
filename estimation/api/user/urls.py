from django.urls import path
from rest_framework.routers import DefaultRouter

from estimation.api.user import views

router = DefaultRouter()
router.register('wtf-data', views.WTFMethodDataAPI)
router.register('wb-data', views.WBMethodDataAPI)

urlpatterns = [
    path('wtf/', views.WTFMethodAPIView.as_view()),
    path('wb/', views.WBMethodAPIView.as_view())
]

urlpatterns += router.urls


