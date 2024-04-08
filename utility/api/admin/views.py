from drf_spectacular.utils import extend_schema
from rest_framework import views, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from . import serializers
from ...models import GlobalSettings


class GlobalSettingsAPI(views.APIView):
    permission_classes = [IsAdminUser, ]

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer},
        request=serializers.GlobalSettingsSerializer
    )
    def get(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(global_settings)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: serializers.GlobalSettingsSerializer},
        request=serializers.GlobalSettingsSerializer
    )
    # @extend_schema(request=serializers.GlobalSettingsSerializer)
    def post(self, request):
        global_settings = GlobalSettings.objects.first()
        serializer = serializers.GlobalSettingsSerializer(data=request.data, instance=global_settings)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
