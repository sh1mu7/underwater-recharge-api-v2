from rest_framework import serializers

from ...models import GlobalSettings


class UserWebsiteInfoSerializer(serializers.ModelSerializer):
    large_logo_url = serializers.CharField(source='get_large_logo_url', read_only=True)
    small_logo_url = serializers.CharField(source='get_small_logo_url', read_only=True)

    class Meta:
        model = GlobalSettings
        fields = '__all__'
