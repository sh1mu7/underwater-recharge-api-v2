from rest_framework import status, viewsets, mixins, response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from coreapp.permissions import IsUser
from . import serializers
from .serializers import WTFMethodSerializer, WBMethodSerializer
from ... import constants
from ...models import WTFMethod, SPYieldData, QData, WBMethodData, ClimateDataPMFull, ClimateDataPMSH, Temperature
from ...utils import eto_methods
from ...utils.calculate_yearly_recharge import calculate_yearly_recharge
from ...utils.eto_methods import hargreaves_method


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
            rlc = serializer.validated_data.get('rlc')
            rp = serializer.validated_data.get('rp')
            classification = serializer.validated_data.get('classification')
            eto_method = serializer.validated_data.get('eto_method')
            latitude = serializer.validated_data.get('latitude')
            temperature_data = serializer.validated_data.get('temperature')
            climatic_data_pm_full = serializer.validated_data.get('climatic_data_pm_full', None)
            climatic_data_pm_sh = serializer.validated_data.get('climatic_data_pm_sh')
            elevation = serializer.validated_data.get('elevation')
            c_value = serializer.validated_data.get('c_value')
            rs_value = serializer.validated_data.get('rs_value')
            rh_value = serializer.validated_data.get('rh_value')
            t_mean_value = serializer.validated_data.get('t_mean_value')
            p_value = serializer.validated_data.get('p_value')
            kc_value = serializer.validated_data.get('kc_value')
            cn_value = serializer.validated_data.get('cn_value')
            recharge_rate = serializer.validated_data.get('recharge_rate')
            land_use_area = serializer.validated_data.get('land_use_area')
            print(land_use_area)
            for L, row in enumerate(land_use_area, 1):
                SM_L = sum(row.values())
                ER_L = 100 - SM_L
                if -5 <= ER_L <= 0:
                    land_use_area[L - 1]["a7"] -= ER_L
                elif 0 < ER_L <= 5:
                    land_use_area[L - 1]["a7"] += ER_L
                else:
                    return response.Response(
                        {"error": f"Sum of land-use components must be equal to 100, Line number {L}, Stop"},
                        status=status.HTTP_400_BAD_REQUEST)

                    # Initialize variables for summing up ETa

            YETO = None
            if eto_method == constants.ETO_METHOD_CHOICES.FAO_COMBINED_PM_METHOD:
                try:
                    climate_data_instances = [ClimateDataPMFull.objects.create(**data) for data in
                                              climatic_data_pm_full]
                    YETO = eto_methods.fao_combined_pm_method(latitude, elevation, climatic_data_pm_full)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, latitude=latitude,
                                                     user=self.request.user)
                    wb.climate_data_full.set(climate_data_instances)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.PM_SH:
                try:
                    climate_data_instances = [ClimateDataPMSH.objects.create(**data) for data in
                                              climatic_data_pm_sh]
                    YETO = eto_methods.pm_method_sh(latitude, elevation, climatic_data_pm_sh)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation,
                                                     latitude=latitude, user=self.request.user)
                    wb.climate_data_pm_sh.set(climate_data_instances)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.PM_NO_SH_RS:
                try:
                    climate_data_instances = [ClimateDataPMSH.objects.create(**data) for data in
                                              climatic_data_pm_sh]
                    YETO = eto_methods.pm_method_no_rs_sh(latitude, elevation, climatic_data_pm_sh)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation,
                                                     latitude=latitude, user=self.request.user)
                    wb.climate_data_pm_sh.set(climate_data_instances)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.FAO_BLANEY_CRIDDLE_METHOD:
                try:
                    # temperature = [Temperature.objects.create(**data) for data in
                    #                temperature_data]
                    YETO = eto_methods.fao_blaney_criddle_method(latitude, c_value, p_value, t_mean_value)
                    wb = WBMethodData.objects.create(eto_method=eto_method, c_values=c_value,
                                                     latitude=latitude, user=self.request.user)
                    # wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.MAKKINK_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.makkink_method(latitude, elevation, rs_value, temperature_data)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.HARGREAVES_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.hargreaves_method(latitude, temperature_data)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.HANSEN_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.hansen_method(latitude, elevation, rs_value, temperature_data)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.TURC_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.turc_method(rs_value, rh_value, temperature_data)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.PRIESTLEY_TAYLOR_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.priestley_taylor_method(latitude, elevation, rs_value, temperature_data)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.ABTEW_METHOD:
                try:
                    # temperature = [Temperature.objects.create(**data) for data in
                    #                temperature_data]
                    YETO = eto_methods.abtew_method(c_value, rs_value)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user, c_values=c_value)
                    # wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            elif eto_method == constants.ETO_METHOD_CHOICES.DE_BRUIN_METHOD:
                try:
                    temperature = [Temperature.objects.create(**data) for data in
                                   temperature_data]
                    YETO = eto_methods.de_bruin_method(rs_value, temperature_data, latitude, elevation)
                    wb = WBMethodData.objects.create(eto_method=eto_method, elevation=elevation, rs_value=rs_value,
                                                     latitude=latitude, user=self.request.user, c_values=c_value)
                    wb.temperature.set(temperature)
                    wb.save()
                except ValidationError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print('Not implemented yet')
                YETO = 'Not implemented yet'
            if YETO is not None:
                print("ET0 (Yearly):", YETO)
            v_sum_etp = 0
            v_sum_eta = 0
            for row in land_use_area:
                # Extract the area values
                a1, a2, a3, a4 = row['a1'], row['a2'], row['a3'], row['a4']

                # Calculate the total area for normalization
                total_area = a1 + a2 + a3 + a4

                # Calculate ETa for each land use area
                for kc_value, cn_value in zip(kc_value, cn_value):
                    for k in range(1, 5):
                        # Assuming Ark, A, and Pr are available
                        # Replace them with actual values or calculations
                        Ark = row[f'a{k}']
                        A = total_area / 100  # Normalize total area to percentage
                        Pr = 100  # Placeholder value for precipitation (replace with actual value)
                        kc_a = kc_value.get(f'kc_a{k}')
                        cn = cn_value.get(f'cn{k}')

                        # Calculate ETrk using ETo and Kc values (here I'm just using kc_a1 for demonstration)
                        ETrk = YETO * kc_a

                        # Sum up ETo for the current area expressed in volume (m3)
                        v_sum_etp += (ETrk * 10) * (Ark * A * 10)

                        # Calculate ETark based on precipitation and CN value (here I'm just using cn1 for demonstration)
                        if ETrk <= Pr:
                            ETark = Pr
                        else:
                            S = (1000 / cn) - 10
                            ajk = (Pr - ETrk - 0.2 * S) ** 2
                            bjk = (Pr - ETrk + 0.8 * S)
                            ETark = ajk / bjk
                        v_sum_eta += (ETark * 10) * (Ark * A * 10)
                        print(f'v_sum_eta (runoff_) = {v_sum_eta}')
                v_sum_ro = 0
                # Loop through each row (j)
                for j, row in enumerate(land_use_area):
                    # Loop through the first four land-use category areas (k = 1 to 4)
                    for k in range(1, 5):
                        # Extract area and precipitation values for the current land-use area
                        Ark = row[f'a{k}']
                        Pj = p_value[j]
                        ETajk = t_mean_value[j]  # Assuming ET values are available corresponding to each land-use area

                        # Extract CN value for the current land-use area
                        CNjk = c_value[j][f'cn{k}']

                        # Calculate surface storage (Sjk)
                        Sjk = (1000 / CNjk) - 10

                        # Calculate ajk and bjk
                        ajk = (Pj - ETajk - 0.2 * Sjk) ** 2
                        bjk = (Pj - ETajk + 0.8 * Sjk)

                        # Calculate Qjk (runoff)
                        Qjk = ajk / bjk

                        # Set Rojk (runoff in mm depth)
                        Rojk = Qjk

                        # Sum up Rojk in volume (m^3)
                        VRojk = (Rojk * 10) * (Ark * A * 10)
                        v_sum_ro += VRojk

                        print(f'v_sum_ro (runoff_volumes) = {v_sum_ro}')

                Sum_VRe = 0

                for j in range(36):
                    for k in range(4):
                        Ajk = land_use_area[j]["a" + str(k + 1)]
                        # Assuming values for ETajk and R0jk for demonstration purposes
                        ETajk = 10  # Example value, replace with actual data
                        R0jk = 5  # Example value, replace with actual data
                        QOutjk = ETajk + R0jk
                        Pk = p_value[j]
                        if QOutjk < Pk:
                            Rejk = Pk - QOutjk
                            VRejk = Rejk * 10 * Ajk * 10
                        else:
                            VRejk = 0
                        Sum_VRe += VRejk

                # Total normal (WB) recharge in volume _V-ReN
                V_ReN = Sum_VRe
            Sum_VRe = 0

            for j in range(36):
                for k in range(4):
                    Ajk = land_use_area[j]["a" + str(k + 1)]
                    ETajk = 10  # Example value, replace with actual data
                    R0jk = 5  # Example value, replace with actual data
                    QOutjk = ETajk + R0jk
                    Pk = p_value[j]
                    if QOutjk < Pk:
                        Rejk = Pk - QOutjk
                        VRejk = Rejk * 10 * Ajk * 10
                    else:
                        VRejk = 0
                    Sum_VRe += VRejk

            # Total normal (WB) recharge in volume _V-ReN
            V_ReN = Sum_VRe
            io_recharge = [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

            # Reading components from io_recharge
            SumRQ = sum([sum(r.values()) for r in io_recharge])

            # Reading/Calculating Recharge from recharge_rate
            RP_values = [r["re_pervious"] for r in recharge_rate]
            RW_values = [r["re_water_body"] for r in recharge_rate]

            SumPW = sum(
                [(RP_values[i] * land_use_area[i]["a5"] * 10 + RW_values[i] * land_use_area[i]["a6"] * 10) for i in
                 range(36)])

            # Total Recharge/discharge from “very pervious & wetland/flooded” areas= FRD
            FRD = SumPW

            # Sum up “All recharges (m3) [normal land + other land]” = Actual Recharge
            VSum_Ra = V_ReN + FRD

            # Sum-up Rainfall_ check the Rainfall Table, data position
            Sum_P = sum(p_value)

            # First, Calculate recharge depth from Recharge vol. (m3)
            # Rad = Actual recharge depth (mm), Ro= runoff depth (mm)
            A = sum([sum(area.values()) for area in land_use_area])  # Total area
            Rad = (VSum_Ra / A) * 0.001  # Assuming conversion factor for volume to depth
            Ro = 0  # Assuming Ro for demonstration purposes, replace with actual data if available

            # Considering Recharge limiting conditions_
            Answer = 1  # Example value, replace with actual data if available
            RF = 0.9  # Example value, replace with actual data if available

            if Answer == 1:
                Rad *= RF

            # Recharge amount (mm), Ratio of Recharge(Ra) and rainfall(P), Ratio of Runoff (Ro) and rainfall
            # Aridity Index (AI) = P/ETp
            Ratio_Ra_P = Rad / Sum_P
            Ratio_Ro_P = Ro / Sum_P
            AI = Sum_P / sum(data["t_mean_value"])

            # Recharge as a percentage of Rainfall is: PRa
            # Runoff as a percentage of Rainfall is: PRo
            PRa = 100 * Rad / Sum_P
            PRo = 100 * Ro / Sum_P

            # Compare_ Yearly Rainfall, Yearly Recharge
            # Check for Accuracy_ if needed, error message
            if PRa > 40:
                print("The Recharge as a percentage of Rainfall is too high! Please Check the input Data")
            else:
                print("Yearly Rainfall (mm) =", Sum_P)
                print("Yearly Recharge (mm) =", Rad)
                print("Yearly Runoff (mm) =", Ro)
                print("Yearly Recharge as a percentage of Precipitation =", PRa)
                print("Yearly Runoff as a percentage of Rainfall =", PRo)
                print("Aridity Index (AI) =", AI)
                print(
                    ".............................................................................................................")
                print("End of Calculation")
            result = {
                'message': 'Calculation performed successfully',
                'Yearly eto calculation': YETO
            }

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WTFMethodDataAPI(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.WTFDataSerializer
    permission_classes = [IsUser]
    queryset = WTFMethod.objects.all()

    def get_queryset(self):
        queryset = WTFMethod.objects.filter(user=self.request.user)
        return queryset
