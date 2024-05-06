from drf_spectacular.utils import extend_schema
from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import serializers
from ...models import GlobalSettings


class PublicInfo(views.APIView):
    permission_classes = [AllowAny, ]

    @extend_schema(
        responses={200: serializers.PublicWebsiteInfoSerializer}
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.PublicWebsiteInfoSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)
