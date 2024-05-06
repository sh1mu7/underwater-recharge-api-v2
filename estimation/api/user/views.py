from rest_framework import status, viewsets, mixins, response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from coreapp.permissions import IsUser
from . import serializers
from .serializers import WTFMethodSerializer, WBMethodSerializer
from .. import filters
from ... import constants
from ...models import WTFMethod, SPYieldData, QData, WBMethodData, EtoRsData, EtoShData, Temperature, CValue, PValue, \
    TMeanValue, RHValue, CropCoefficient, RechargeRate, CurveNumber, SolarRadiation, LandUseArea
from ...utils import eto_methods
from ...utils.calculate_yearly_recharge import calculate_yearly_recharge
from ...utils.eto_methods import hargreaves_method, eto_method_validation
from ...utils.wb_method_utils import process_land_use_data_with_cn_kc, calculate_eto_method, calculate_volumes, \
    calculate_recharge
from django_filters import rest_framework as dj_filter


class WTFMethodAPIView(APIView):
    serializer_class = WTFMethodSerializer
    permission_classes = [IsUser]

    def post(self, request, *args, **kwargs):
        serializer = WTFMethodSerializer(data=request.data)
        if serializer.is_valid():
            catchment_area = serializer.validated_data['catchment_area']
            wt_max = serializer.validated_data['wt_max']
            wt_min = serializer.validated_data['wt_min']
            num_layers = serializer.validated_data['num_layers']
            precipitation = serializer.validated_data.get('precipitation', None)
            Q_data = serializer.validated_data['Q_data']
            sp_yield_data = serializer.validated_data['sp_yield_data']

            for entry in Q_data:
                for key, value in entry.items():
                    entry[key] = float(value)

            # Convert string values to floats in sp_yield_data
            for entry in sp_yield_data:
                entry['layer_height'] = float(entry['layer_height'])
                entry['sp_yield_percentage'] = float(entry['sp_yield_percentage'])

            result = calculate_yearly_recharge(catchment_area, wt_max, wt_min, num_layers, sp_yield_data, precipitation,
                                               Q_data)

            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            wtf_data_object = WTFMethod.objects.create(user=self.request.user, catchment_area=catchment_area,
                                                       wt_max=wt_max, wt_min=wt_min, num_layers=num_layers,
                                                       is_precipitation_given=True, precipitation=precipitation,
                                                       yearly_recharge=result['YearlyRecharge'], ratio=result['Ratio'])

            q_data_instances = [QData.objects.create(wtf=wtf_data_object, **entry) for entry in Q_data]
            sp_yield_data_instances = [SPYieldData.objects.create(wtf=wtf_data_object, **entry) for entry in
                                       sp_yield_data]
            wtf_data_object.save()
            return Response({'result': result}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WBMethodAPIView(APIView):
    serializer_class = WBMethodSerializer
    permission_classes = [IsUser]

    def post(self, request, *args, **kwargs):
        serializer = WBMethodSerializer(data=request.data)
        if serializer.is_valid():
            catchment_area = serializer.validated_data.get('catchment_area')
            latitude = serializer.validated_data.get('latitude')
            elevation = serializer.validated_data.get('elevation')
            rlc = serializer.validated_data.get('rlc')
            rp = serializer.validated_data.get('rp')
            classification = serializer.validated_data.get('classification')
            eto_method = serializer.validated_data.get('eto_method')
            temperature = serializer.validated_data.get('temperature')
            eto_rs_data = serializer.validated_data.get('eto_rs_data', None)
            eto_sh_data = serializer.validated_data.get('eto_sh_data')
            c_value = serializer.validated_data.pop('c_value', [])
            solar_radiation = serializer.validated_data.get('solar_radiation')
            rh_value = serializer.validated_data.get('rh_value')
            t_mean_value = serializer.validated_data.get('t_mean_value')
            p_value = serializer.validated_data.get('p_value')
            kc_value = serializer.validated_data.get('kc_value')
            cn_value = serializer.validated_data.get('cn_value')
            recharge_rate = serializer.validated_data.get('recharge_rate')
            land_use_area = serializer.validated_data.pop('land_use_area')
            process_land_use_data_with_cn_kc(land_use_area, kc_value, cn_value)
            yeto = calculate_eto_method(eto_method, latitude, elevation, eto_rs_data, eto_sh_data, c_value, p_value,
                                        t_mean_value, solar_radiation, rh_value, temperature)
            v_ren = calculate_volumes(land_use_area, kc_value, cn_value, p_value, t_mean_value, yeto)
            recharge_data = calculate_recharge(land_use_area, recharge_rate, p_value, v_ren, t_mean_value, yeto)
            wb_method_data = WBMethodData.objects.create(
                user=self.request.user,
                catchment_area=serializer.validated_data.get('catchment_area'),
                latitude=serializer.validated_data.get('latitude'),
                elevation=serializer.validated_data.get('elevation'), rlc=serializer.validated_data.get('rlc'), rp=rp,
                classification=classification, eto_method=serializer.validated_data.get('eto_method')
            )

            if temperature is not None:
                for temp in temperature:
                    temperature_instance = Temperature.objects.create(**temp)
                    wb_method_data.temperature.add(temperature_instance)

            if cn_value is not None:
                for value in cn_value:
                    cn_value_instance = CurveNumber.objects.create(**value)
                    wb_method_data.cn_value.add(cn_value_instance)

            if kc_value is not None:
                for value in kc_value:
                    kc_value_instance = CropCoefficient.objects.create(**value)
                    wb_method_data.kc_value.add(kc_value_instance)

            if c_value is not None:
                for value in c_value:
                    c_value_instance = CValue.objects.create(value=value)
                    wb_method_data.c_value.add(c_value_instance)

            if eto_rs_data is not None:
                for value in eto_rs_data:
                    eto_rs_instance = EtoRsData.objects.create(**value)
                    wb_method_data.eto_rs_data.add(eto_rs_instance)

            if eto_sh_data is not None:
                for value in eto_sh_data:
                    eto_sh_instance = EtoShData.objects.create(**value)
                    wb_method_data.eto_sh_data.add(eto_sh_instance)

            if p_value is not None:
                for value in p_value:
                    p_value_instance = PValue.objects.create(value=value)
                    wb_method_data.p_value.add(p_value_instance)

            if t_mean_value is not None:
                for value in t_mean_value:
                    t_mean_value_instance = TMeanValue.objects.create(value=value)
                    wb_method_data.t_mean_value.add(t_mean_value_instance)

            if rh_value is not None:
                for value in rh_value:
                    rh_value_instance = RHValue.objects.create(value=value)
                    wb_method_data.rh_value.add(rh_value_instance)

            if recharge_rate is not None:
                for value in recharge_rate:
                    recharge_rate_instance = RechargeRate.objects.create(**value)
                    wb_method_data.recharge_rate.add(recharge_rate_instance)

            if solar_radiation is not None:
                for value in solar_radiation:
                    solar_radiation_instance = SolarRadiation.objects.create(value=value)
                    wb_method_data.solar_radiation.add(solar_radiation_instance)

            if land_use_area is not None:
                for value in land_use_area:
                    filtered_data = {key: value[key] for key in value.keys() if
                                     key in ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7']}
                    land_use_area_instance = LandUseArea.objects.create(**filtered_data)
                    wb_method_data.land_use_area.add(land_use_area_instance)

            return Response(recharge_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WTFMethodDataAPI(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.WTFDataSerializer
    permission_classes = [IsUser]
    queryset = WTFMethod.objects.all()

    def get_queryset(self):
        queryset = WTFMethod.objects.filter(user=self.request.user)
        return queryset


class WBMethodDataAPI(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.WBMethodDataSerializer
    permission_classes = [IsUser]
    queryset = WBMethodData.objects.all()
    filter_backends = (dj_filter.DjangoFilterBackend,)
    filterset_class = filters.WBFilter

    def get_queryset(self):
        queryset = WBMethodData.objects.filter(user=self.request.user)
        return queryset
