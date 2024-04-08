from rest_framework import serializers

from estimation import constants
from estimation.models import QData, SPYieldData, WTFMethod, WBMethodData, ClimateDataPMFull, ClimateDataPMSH, \
    Temperature


class QDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = QData
        fields = ['QP_n', 'QB_n', 'Qin_n', 'Qout_n', 'Qr_n']


class SPYieldDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPYieldData
        fields = ['layer_height', 'sp_yield_percentage']


class WTFDataSerializer(serializers.ModelSerializer):
    sp_yield_data = SPYieldDataSerializer(many=True)
    Q_data = QDataSerializer(many=True)

    class Meta:
        model = WTFMethod
        fields = ['catchment_area', 'wt_max', 'wt_min', 'time_period', 'num_layers',
                  'is_precipitation_given', 'precipitation_percentage', 'Q_data', 'sp_yield_data']


class WTFMethodSerializer(serializers.ModelSerializer):
    sp_yield_data = SPYieldDataSerializer(many=True, read_only=False)
    Q_data = QDataSerializer(many=True, read_only=False)

    class Meta:
        model = WTFMethod
        fields = ['catchment_area', 'wt_max', 'wt_min', 'time_period', 'num_layers',
                  'is_precipitation_given', 'precipitation_percentage', 'Q_data', 'sp_yield_data']

    def validate(self, data):
        """
        Additional validation for the serializer fields.
        """
        num_layers = data.get('num_layers')
        sp_yield_data = data.get('sp_yield_data', [])
        print(f'num_layers: {num_layers}, sp_yield_data: {len(sp_yield_data)}')
        if num_layers is not None and len(sp_yield_data) != num_layers:
            raise serializers.ValidationError("Number of layers does not match the provided data.")
        input_values = data.get('Q_data', [])
        print(len(input_values))
        if len(input_values) != 12:
            raise serializers.ValidationError("Exactly 12 sets of input values are required.")
        return data

    def create(self, validated_data):
        sp_yield_data = validated_data.pop('sp_yield_data')
        q_data = validated_data.pop('Q_data')

        print("Creating WTFMethod instance with data:", validated_data)
        # Create WTFMethod instance
        wtf_method = WTFMethod.objects.create(**validated_data)

        # Create SPYieldData instances
        for sp_yield in sp_yield_data:
            print("Creating SPYieldData instance with data:", sp_yield)
            SPYieldData.objects.create(wtf_method=wtf_method, **sp_yield)

        # Create QData instances
        for q in q_data:
            print("Creating QData instance with data:", q)
            QData.objects.create(wtf_method=wtf_method, **q)

        print("WTFMethod instance created successfully:", wtf_method)
        return wtf_method


class TemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temperature
        fields = '__all__'


class ClimateDataFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateDataPMFull
        fields = '__all__'

        extra_kwargs = {
            'SR_r': {'required': False},
        }


class ClimateDataPMSHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClimateDataPMSH
        fields = '__all__'


class InflowOutflowRechargeSerializer(serializers.Serializer):
    rr = serializers.FloatField()
    rc = serializers.FloatField()
    rd = serializers.FloatField()


class LandUseAreaSerializer(serializers.Serializer):
    a1 = serializers.FloatField()
    a2 = serializers.FloatField()
    a3 = serializers.FloatField()
    a4 = serializers.FloatField()
    a5 = serializers.FloatField()
    a6 = serializers.FloatField()
    a7 = serializers.FloatField()


class CropCoefficientSerializer(serializers.Serializer):
    kc_a1 = serializers.FloatField()
    kc_a2 = serializers.FloatField()
    kc_a3 = serializers.FloatField()
    kc_a4 = serializers.FloatField()


class CurveNumberSerializer(serializers.Serializer):
    cn1 = serializers.IntegerField(min_value=0, max_value=100)
    cn2 = serializers.IntegerField(min_value=0, max_value=100)
    cn3 = serializers.IntegerField(min_value=0, max_value=100)
    cn4 = serializers.IntegerField(min_value=0, max_value=100)


class WBMethodSerializer(serializers.Serializer):
    catchment_area = serializers.FloatField(required=False)
    rlc = serializers.ChoiceField(choices=constants.ClassificationChoices.choices, required=False)
    rp = serializers.FloatField(required=False)
    classification = serializers.ChoiceField(choices=constants.ClassificationChoices.choices, required=False)
    eto_method = serializers.ChoiceField(choices=constants.ETO_METHOD_CHOICES)
    temperature = TemperatureSerializer(many=True, required=False)
    c_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    rh_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)

    rs_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    latitude = serializers.FloatField(required=False)
    climatic_data_pm_full = ClimateDataFullSerializer(many=True, required=False)
    climatic_data_pm_sh = ClimateDataPMSHSerializer(many=True, required=False)
    elevation = serializers.FloatField(required=False)
    # New WB
    land_use_area = LandUseAreaSerializer(many=True, required=True)
    t_mean_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    p_value = serializers.ListSerializer(child=serializers.FloatField(required=False), required=False)
    kc_value = CropCoefficientSerializer(many=True, required=False)
    cn_value = CurveNumberSerializer(many=True, required=False)
    io_recharge = InflowOutflowRechargeSerializer(many=True, required=False)
    #
    # def validate(self, data):
    #     """
    #     Validate method for WBMethodSerializer.
    #     """
    #     climatic_data_pm_full = data.get('climatic_data_pm_full', [])
    #     climatic_data_pm_sh = data.get('climatic_data_pm_sh', [])
    #     temperature = data.get('temperature')
    #     eto_method = data.get('eto_method')
    #     rs_value = data.get('rs_value')
    #     rh_value = data.get('rh_value')
    #     c_value = data.get('c_value')
    #     latitude = data.get('latitude')
    #     elevation = data.get('elevation')
    #     if eto_method == constants.ETO_METHOD_CHOICES.FAO_COMBINED_PM_METHOD:
    #         for period_data in climatic_data_pm_full:
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
    #         for period_data in climatic_data_pm_sh:
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
    #         for period_data in climatic_data_pm_sh:
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
