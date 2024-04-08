from django_filters import rest_framework as dj_filters
from coreapp.models import User


class UserFilter(dj_filters.FilterSet):
    class Meta:
        model = User
        fields = ['email', 'mobile', 'first_name', 'last_name']
