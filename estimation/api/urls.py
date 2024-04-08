from django.urls import path, include

urlpatterns = [
    path('user/', include('estimation.api.user.urls'))
]
