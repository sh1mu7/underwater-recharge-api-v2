from drf_spectacular.utils import extend_schema
from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from coreapp.permissions import IsUser
from . import serializers
from ...models import GlobalSettings


# Currency, FAQ, Banner, SearchResult, Refund, EmailSubscription)


class PublicInfo(views.APIView):
    permission_classes = [IsUser, ]

    @extend_schema(
        responses={200: serializers.UserWebsiteInfoSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.UserWebsiteInfoSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
