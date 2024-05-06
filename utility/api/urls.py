from django.urls import path, include

urlpatterns = [
    path("admin/", include("utility.api.admin.urls")),
    path("user/", include("utility.api.user.urls")),
    path("public/", include("utility.api.public.urls")),

]
