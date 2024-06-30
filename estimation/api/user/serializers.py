from rest_framework import serializers

from estimation import constants
from estimation.models import QOutData, SPYieldData, WTFMethod, WBMethodData, EtoRsData, Temperature, EtoShData, \
    LandUseArea, CropCoefficient, CurveNumber, RechargeRate, CValue, PValue, RHValue, SolarRadiation, TMeanValue, \
    EtoData, OutFlow, QinData, ReWaterBody
from estimation.utils.eto_methods import eto_method_validation


class QOutDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = QOutData
        fields = ['pump', 'base', 'gw_out']


class QinDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = QinData
        fields = ('value',)


class SPYieldDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPYieldData
        fields = ['layer_height', 'sp_yield_percentage']


class WTFDataSerializer(serializers.ModelSerializer):
    sp_yield_data = SPYieldDataSerializer(many=True, read_only=True)
    wtf_q_out_data = QOutDataSerializer(many=True, read_only=True)
    q_in = QinDataSerializer(many=True, read_only=True)

    class Meta:
        model = WTFMethod
        fields = ['id', 'catchment_area', 'wt_max', 'wt_min', 'num_layers', 'q_in',
                  'is_precipitation_given', 'precipitation',
                  'wtf_q_out_data', 'sp_yield_data']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        q_in_values = instance.q_in.all().values_list('value', flat=True)
        representation['q_in'] = list(q_in_values)
        return representation


class WTFMethodSerializer(serializers.ModelSerializer):
    sp_yield_data = SPYieldDataSerializer(many=True, read_only=False)
    q_out = QOutDataSerializer(many=True, read_only=False)
    q_in = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)

    class Meta:
        model = WTFMethod
        fields = ['catchment_area', 'wt_max', 'wt_min', 'num_layers', 'precipitation', 'q_out', 'q_in', 'sp_yield_data']

    def validate(self, data):
        """
        Additional validation for the serializer fields.
        """
        num_layers = data.get('num_layers')
        sp_yield_data = data.get('sp_yield_data', [])
        if num_layers is not None and len(sp_yield_data) != num_layers:
            raise serializers.ValidationError("Number of layers does not match the provided data.")
        input_values = data.get('q_out', [])
        print(len(input_values))
        if len(input_values) != 12:
            raise serializers.ValidationError("Exactly 12 sets of input values are required.")
        return data

    def create(self, validated_data):
        sp_yield_data = validated_data.pop('sp_yield_data')
        q_data = validated_data.pop('q_out')
        q_in_data = validated_data.pop('q_in')
        print("Creating WTFMethod instance with data:", validated_data)
        # Create WTFMethod instance
        wtf_method = WTFMethod.objects.create(**validated_data)

        # Create SPYieldData instances
        for sp_yield in sp_yield_data:
            print("Creating SPYieldData instance with data:", sp_yield)
            SPYieldData.objects.create(wtf_method=wtf_method, **sp_yield)
        # for q_in in q_in_data:
        #     print("Creating SPYieldData instance with data:", q_in)
        #     QinData.objects.create(wtf_method=wtf_method, **q_in)

        # Create QOutData instances
        for q in q_data:
            print("Creating QOutData instance with data:", q)
            QOutData.objects.create(wtf_method=wtf_method, **q)

        print("WTFMethod instance created successfully:", wtf_method)
        return wtf_method


class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temperature
        fields = '__all__'


class EtoRsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtoRsData
        fields = '__all__'

        extra_kwargs = {
            'SR_t': {'required': False},
        }


class EtoShDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtoShData
        fields = '__all__'


class InflowOutflowRechargeSerializer(serializers.Serializer):
    rr = serializers.FloatField()
    rc = serializers.FloatField()
    rd = serializers.FloatField()


class LandUseAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandUseArea
        fields = '__all__'


class RechargeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechargeRate
        fields = '__all__'


class OutFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutFlow
        fields = ('out_dr', 'out_other')


class CropCoefficientSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropCoefficient
        fields = '__all__'


class CurveNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurveNumber
        fields = '__all__'


class WBMethodSerializer(serializers.Serializer):
    catchment_area = serializers.FloatField(required=False)
    rlc = serializers.ChoiceField(choices=constants.ClassificationChoices.choices, required=False)
    rp = serializers.FloatField(required=False)
    classification = serializers.ChoiceField(choices=constants.ClassificationChoices.choices, required=False)
    eto_method = serializers.ChoiceField(choices=constants.ETO_METHOD_CHOICES)
    temperature = TemperatureSerializer(many=True, required=False)
    latitude = serializers.FloatField(required=False)
    c_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    rh_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    solar_radiation = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    t_mean_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    p_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    re_water_body = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    kc_value = CropCoefficientSerializer(many=True, required=False)
    cn_value = CurveNumberSerializer(many=True, required=False)
    eto_rs_data = EtoRsDataSerializer(many=True, required=False)
    eto_sh_data = EtoShDataSerializer(many=True, required=False)
    elevation = serializers.FloatField(required=False)
    land_use_area = LandUseAreaSerializer(many=True, required=True)
    recharge_rate = RechargeRateSerializer(many=True, required=False)
    outflow = OutFlowSerializer(many=True, required=False)
    rf = serializers.FloatField(required=False)
    rf_option = serializers.BooleanField(required=False)

    def validate(self, attrs):
        eto_method_validation(attrs)
        return attrs

    # def validate(self, data):
    #     """
    #     Validate method for WBMethodSerializer.
    #     """
    #     eto_rs_data = data.get('eto_rs_data', [])
    #     eto_sh_data = data.get('eto_sh_data', [])
    #     temperature = data.get('temperature')
    #     eto_method = data.get('eto_method')
    #     rs_value = data.get('rs_value')
    #     rh_value = data.get('rh_value')
    #     c_value = data.get('c_value')
    #     latitude = data.get('latitude')
    #     elevation = data.get('elevation')
    #     if eto_method == constants.ETO_METHOD_CHOICES.FAO_COMBINED_PM_METHOD:
    #         for period_data in eto_rs_data:
    #             P_r = period_data.get('P_r', 0)
    #             Tmax_r = period_data.get('Tmax_r', 0)
    #             Tmin_r = period_data.get('Tmin_r', 0)
    #             RH_r = period_data.get('RH_r', 0)
    #             WS_r = period_data.get('WS_r', 0)
    #             SR_r = period_data.get('SR_r', 0)
    #
    #             print(f'RH_r = {P_r}')
    #             if P_r > 1000:
    #                 raise serializers.ValidationError(f'Precipitation is > 1000: {P_r}. Check the data.')
    #             elif P_r < 0:
    #                 raise serializers.ValidationError(f'Precipitation is < 0: {P_r}. Check the data.')
    #
    #             if Tmax_r > 50:
    #                 raise serializers.ValidationError(f'Max. Temp. is > 50: {Tmax_r}. Check the data.')
    #             elif Tmin_r < -20:
    #                 raise serializers.ValidationError(f'Min. Temp. is < -20: {Tmin_r}. Check the data.')
    #
    #             if RH_r > 99:
    #                 raise serializers.ValidationError(f'RH > 99: {RH_r}. Check the data.')
    #             elif RH_r < 25:
    #                 raise serializers.ValidationError(f'RH < 25: {RH_r}. Check the data.')
    #
    #             if SR_r > 30:
    #                 raise serializers.ValidationError(f'Solar Radiation > 30: {SR_r}. Check the data.')
    #             elif SR_r < 0:
    #                 raise serializers.ValidationError(f'Solar Radiation < 0: {SR_r}. Check the data.')
    #
    #             if WS_r > 5:
    #                 raise serializers.ValidationError(f'Wind speed > 5: {WS_r}. Check the data.')
    #             elif WS_r < 0:
    #                 raise serializers.ValidationError(f'Wind speed < 0: {WS_r}. Check the data.')
    #     elif eto_method == constants.ETO_METHOD_CHOICES.PM_SH:
    #         for period_data in eto_sh_data:
    #             P_r = period_data.get('P_r', 0)
    #             Tmax_r = period_data.get('Tmax_r', 0)
    #             Tmin_r = period_data.get('Tmin_r', 0)
    #             RH_r = period_data.get('RH_r', 0)
    #             WS_r = period_data.get('WS_r', 0)
    #             SH_r = period_data.get('SH_r', 0)
    #
    #             print(f'RH_r = {P_r}')
    #             if P_r > 1000:
    #                 raise serializers.ValidationError(f'Precipitation is > 1000: {P_r}. Check the data.')
    #             elif P_r < 0:
    #                 raise serializers.ValidationError(f'Precipitation is < 0: {P_r}. Check the data.')
    #
    #             if Tmax_r > 50:
    #                 raise serializers.ValidationError(f'Max. Temp. is > 50: {Tmax_r}. Check the data.')
    #             elif Tmin_r < -20:
    #                 raise serializers.ValidationError(f'Min. Temp. is < -20: {Tmin_r}. Check the data.')
    #
    #             if RH_r > 99:
    #                 raise serializers.ValidationError(f'RH > 99: {RH_r}. Check the data.')
    #             elif RH_r < 25:
    #                 raise serializers.ValidationError(f'RH < 25: {RH_r}. Check the data.')
    #
    #             if SH_r > 30:
    #                 raise serializers.ValidationError(f'Solar Radiation > 30: {SH_r}. Check the data.')
    #             elif SH_r < 0:
    #                 raise serializers.ValidationError(f'Solar Radiation < 0: {SH_r}. Check the data.')
    #
    #             if WS_r > 5:
    #                 raise serializers.ValidationError(f'Wind speed > 5: {WS_r}. Check the data.')
    #             elif WS_r < 0:
    #                 raise serializers.ValidationError(f'Wind speed < 0: {WS_r}. Check the data.')
    #     elif eto_method == constants.ETO_METHOD_CHOICES.PM_NO_SH_RS:
    #         for period_data in eto_sh_data:
    #             P_r = period_data.get('P_r', 0)
    #             Tmax_r = period_data.get('Tmax_r', 0)
    #             Tmin_r = period_data.get('Tmin_r', 0)
    #             RH_r = period_data.get('RH_r', 0)
    #             WS_r = period_data.get('WS_r', 0)
    #             SH_r = period_data.get('SH_r', 0)
    #
    #             print(f'RH_r = {P_r}')
    #             if P_r > 1000:
    #                 raise serializers.ValidationError(f'Precipitation is > 1000: {P_r}. Check the data.')
    #             elif P_r < 0:
    #                 raise serializers.ValidationError(f'Precipitation is < 0: {P_r}. Check the data.')
    #
    #             if Tmax_r > 50:
    #                 raise serializers.ValidationError(f'Max. Temp. is > 50: {Tmax_r}. Check the data.')
    #             elif Tmin_r < -20:
    #                 raise serializers.ValidationError(f'Min. Temp. is < -20: {Tmin_r}. Check the data.')
    #
    #             if RH_r > 99:
    #                 raise serializers.ValidationError(f'RH > 99: {RH_r}. Check the data.')
    #             elif RH_r < 25:
    #                 raise serializers.ValidationError(f'RH < 25: {RH_r}. Check the data.')
    #
    #             if SH_r > 30:
    #                 raise serializers.ValidationError(f'Solar Radiation > 30: {SH_r}. Check the data.')
    #             elif SH_r < 0:
    #                 raise serializers.ValidationError(f'Solar Radiation < 0: {SH_r}. Check the data.')
    #
    #             if WS_r > 5:
    #                 raise serializers.ValidationError(f'Wind speed > 5: {WS_r}. Check the data.')
    #             elif WS_r < 0:
    #                 raise serializers.ValidationError(f'Wind speed < 0: {WS_r}. Check the data.')
    #     elif eto_method == constants.ETO_METHOD_CHOICES.FAO_BLANEY_CRIDDLE_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.FAO_BLANEY_CRIDDLE_METHOD:
    #             for temp_data in temperature:
    #                 t_max = temp_data.get('t_max')
    #                 t_min = temp_data.get('t_min')
    #                 if t_min is None or t_max is None:
    #                     raise serializers.ValidationError("Both 't_max' and 't_min' are required for temperature data.")
    #                 if t_min > t_max:
    #                     raise serializers.ValidationError({'t_max': f't_min > t_max: {t_min} > {t_max}'})
    #     elif eto_method == constants.ETO_METHOD_CHOICES.MAKKINK_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.MAKKINK_METHOD:
    #             if len(temperature) and len(rs_value) != 36:
    #                 raise serializers.ValidationError("data should be 36 times ")
    #     elif eto_method == constants.ETO_METHOD_CHOICES.HARGREAVES_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.HARGREAVES_METHOD:
    #             if len(temperature) != 36:
    #                 raise serializers.ValidationError("data should be 36 times ")
    #     elif eto_method == constants.ETO_METHOD_CHOICES.HANSEN_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.HANSEN_METHOD:
    #             if len(temperature) and len(rs_value) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)}",
    #                     code="invalid_data_length"
    #                 )
    #     elif eto_method == constants.ETO_METHOD_CHOICES.TURC_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.TURC_METHOD:
    #             if len(temperature) and len(rs_value) and len(rh_value) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data or RH Data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)} and rs_value: {len(rh_value)}",
    #                     code="invalid_data_length"
    #                 )
    #     elif eto_method == constants.ETO_METHOD_CHOICES.PRIESTLEY_TAYLOR_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.PRIESTLEY_TAYLOR_METHOD:
    #             if len(temperature) and len(rs_value) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)} ",
    #                     code="invalid_data_length"
    #                 )
    #             if latitude and elevation is None:
    #                 raise serializers.ValidationError(f"latitude and elevation can't be None")
    #     elif eto_method == constants.ETO_METHOD_CHOICES.JENSEN_HAISE_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.JENSEN_HAISE_METHOD:
    #             if len(temperature) and len(rs_value) and len(c_value) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)} ",
    #                     code="invalid_data_length"
    #                 )
    #             if latitude and elevation is None:
    #                 raise serializers.ValidationError(f"latitude and elevation can't be None")
    #
    #     elif eto_method == constants.ETO_METHOD_CHOICES.ABTEW_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.ABTEW_METHOD:
    #             if len(rs_value) and len(c_value) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)} ",
    #                     code="invalid_data_length"
    #                 )
    #             if latitude and elevation is None:
    #                 raise serializers.ValidationError(f"latitude and elevation can't be None")
    #
    #     elif eto_method == constants.ETO_METHOD_CHOICES.DE_BRUIN_METHOD:
    #         if eto_method == constants.ETO_METHOD_CHOICES.DE_BRUIN_METHOD:
    #             if len(rs_value) and len(temperature) != 36:
    #                 raise serializers.ValidationError(
    #                     f"Temperature or Rs data is not provided for all 36 days. Check the length of temperature: {len(temperature)} and rs_value: {len(rs_value)} ",
    #                     code="invalid_data_length"
    #                 )
    #             if latitude and elevation is None:
    #                 raise serializers.ValidationError(f"latitude and elevation can't be None")
    #
    #     else:
    #         pass
    #         # raise serializers.ValidationError({'eto_method': 'Invalid eto method.'})
    #     return data


class CValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CValue
        fields = '__all__'


class PValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PValue
        fields = '__all__'


class RHValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = RHValue
        fields = '__all__'


class SolarRadiationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolarRadiation
        fields = '__all__'


class TMeanValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMeanValue
        fields = '__all__'


class EtoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtoData
        fields = ['value', ]


class ReWaterBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReWaterBody
        fields = ['value']


class WBMethodDataSerializer(serializers.ModelSerializer):
    temperature = TemperatureSerializer(many=True)
    kc_value = CropCoefficientSerializer(many=True)
    cn_value = CurveNumberSerializer(many=True)
    eto_rs_data = EtoRsDataSerializer(many=True)
    eto_sh_data = EtoShDataSerializer(many=True)
    land_use_area = LandUseAreaSerializer(many=True)
    recharge_rate = RechargeRateSerializer(many=True)
    c_value = CValueSerializer(many=True)
    p_value = PValueSerializer(many=True)
    rh_value = RHValueSerializer(many=True)
    solar_radiation = SolarRadiationSerializer(many=True)
    t_mean_value = TMeanValueSerializer(many=True)
    eto_list = EtoDataSerializer(many=True)
    outflow = OutFlowSerializer(many=True)
    re_water_body = ReWaterBodySerializer(many=True)

    class Meta:
        model = WBMethodData
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        c_values = [item['value'] for item in representation.pop('c_value', [])]
        p_values = [item['value'] for item in representation.pop('p_value', [])]
        re_water_body = [item['value'] for item in representation.pop('re_water_body', [])]
        rh_values = [item['value'] for item in representation.pop('rh_value', [])]
        eto_list = [item['value'] for item in representation.pop('eto_list', [])]
        solar_radiation_values = [item['value'] for item in representation.pop('solar_radiation', [])]
        t_mean_values = [item['value'] for item in representation.pop('t_mean_value', [])]
        representation['c_value'] = c_values
        representation['p_value'] = p_values
        representation['re_water_body'] = re_water_body
        representation['rh_value'] = rh_values
        representation['solar_radiation'] = solar_radiation_values
        representation['t_mean_value'] = t_mean_values
        representation['eto_list'] = eto_list
        return representation
