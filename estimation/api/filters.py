from django_filters import rest_framework as dj_filters

from estimation.models import WBMethodData


class WBFilter(dj_filters.FilterSet):
    class Meta:
        model = WBMethodData
        fields = ('eto_method',)
