from math import floor

from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import pandas as pd
from estimation import constants
from estimation.models import EtoRsData, EtoShData
from estimation.utils import eto_methods


# def process_land_use_data_with_cn_kc(land_use_area, kc_value, cn_value):
#     if kc_value is None or cn_value is None:
#         return {"error": "kc_value or cn_value is None"}
#     for L, row in enumerate(land_use_area, 0):
#         SM_L = sum(row.values())
#         ER_L = 100 - SM_L
#         if -5 <= ER_L <= 0:
#             land_use_area[L - 1]["a7"] -= ER_L
#         elif 0 < ER_L <= 5:
#             land_use_area[L - 1]["a7"] += ER_L
#         else:
#             return {"error": f"Sum of land-use components must be equal to 100, Line number {L}, Stop"}
#         KC_values = kc_value[L]
#         CN_values = cn_value[L]
#         for k, (CN, KC) in enumerate(zip(CN_values, KC_values), 0):
#             land_use_area[L][f"CN{k}"] = CN
#             land_use_area[L][f"KC{k}"] = KC
#     return land_use_area


def calculate_eto_method(eto_method, latitude, elevation, eto_rs_data, eto_sh_data, c_value, p_value,
                         solar_radiation, rh_value, temperature):
    YETO = None
    eto_list = None
    try:
        if eto_method == constants.ETO_METHOD_CHOICES.FAO_COMBINED_PM_METHOD:
            climate_data_instances = [EtoRsData.objects.create(**data) for data in eto_rs_data]
            YETO, eto_list = eto_methods.fao_combined_pm_method(latitude, elevation, eto_rs_data, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.PM_SH:
            climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.pm_method_sh(latitude, elevation, eto_sh_data, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.PM_NO_SH_RS:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.pm_method_no_rs_sh(latitude, elevation, eto_sh_data, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.FAO_BLANEY_CRIDDLE_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.fao_blaney_criddle_method(latitude, c_value, temperature, p_value)
        elif eto_method == constants.ETO_METHOD_CHOICES.HARGREAVES_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.hargreaves_method(latitude, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.MAKKINK_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.makkink_method(latitude, elevation, solar_radiation, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.HANSEN_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.hansen_method(latitude, elevation, solar_radiation, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.TURC_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.turc_method(solar_radiation, rh_value, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.PRIESTLEY_TAYLOR_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.priestley_taylor_method(latitude, elevation, solar_radiation, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.JENSEN_HAISE_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.jensen_haise_method(c_value, solar_radiation, temperature)
        elif eto_method == constants.ETO_METHOD_CHOICES.ABTEW_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.abtew_method(c_value, solar_radiation)
        elif eto_method == constants.ETO_METHOD_CHOICES.DE_BRUIN_METHOD:
            # climate_data_instances = [EtoShData.objects.create(**data) for data in eto_sh_data]
            YETO, eto_list = eto_methods.de_bruin_method(solar_radiation, temperature, latitude, elevation, c_value)
        else:
            return Response({'error': f"Method {eto_method} is not implemented yet"},
                            status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return YETO, eto_list


# def calculate_volumes(catchment_area, land_use_area, kc_values, cn_values, p_values, temperature, yeto):
#     v_sum_etp = 0
#     v_sum_eta = 0
#     v_sum_ro = 0
#     sum_vre = 0
#
#     for i in range(len(land_use_area)):
#         a1, a2, a3, a4 = land_use_area[i]['a1'], land_use_area[i]['a2'], land_use_area[i]['a3'], land_use_area[i]['a4']
#         total_area = a1 + a2 + a3 + a4
#         kc_value = kc_values[i]
#         cn_value = cn_values[i]
#         for k in range(1, 5):
#             a_k = land_use_area[i][f'a{k}']
#             pr = p_values[i]
#             kc_a = kc_value[f'kc_a{k}']
#             cn = cn_value[f'cn{k}']
#             etrk = yeto * kc_a
#             v_sum_etp += (etrk * 10) * (a_k * total_area * 10)
#             if etrk <= pr:
#                 etark = pr
#             else:
#                 s = ((1000 / cn) - 10) * 10
#
#                 ajk = (pr - etrk - 0.2 * s) ** 2
#                 bjk = (pr - etrk + 0.8 * s)
#                 etark = ajk / bjk
#                 print(f'etark: {etark}')
#             v_sum_eta += (etark * 10) * (a_k * total_area * 10)
#             p_j = p_values[i]
#             tmax = temperature[k]['t_max']
#             tmin = temperature[k]['t_min']
#             et_ajk = (tmax + tmin) / 2
#             cn_jk = cn_values[i][f'cn{k}']
#
#             s_jk = (1000 / cn_jk) - 10
#             ajk = (p_j - et_ajk - 0.2 * s_jk) ** 2
#             bjk = (p_j - et_ajk + 0.8 * s_jk)
#             # print(f'p_j: {p_j}, cn_{i}_{k}: {cn_jk}, sjk_{i}_{k}: {s_jk}, ajk_{i}_{k}: {ajk}, bjk_{i}_{k}: {bjk}, et_ajk_{i}_{k}: {et_ajk}')
#             q_jk = ajk / bjk
#             ro_jk = q_jk
#             v_sum_ro += (ro_jk * 10) * (land_use_area[i][f'a{k}'] * total_area * 10)
#
#     for i in range(len(p_values)):
#         for k in range(4):
#             a_jk = land_use_area[i][f'a{k + 1}']
#             et_ajk = 10
#             r0_jk = 5
#             q_out_jk = et_ajk + r0_jk
#             p_k = p_values[i]
#             if q_out_jk < p_k:
#                 re_jk = p_k - q_out_jk
#                 v_re_jk = re_jk * 10 * a_jk * 10
#             else:
#                 v_re_jk = 0
#             sum_vre += v_re_jk
#
#     v_ren = sum_vre
#     return v_ren
#
#
# def calculate_recharge(land_use_area, recharge_rate, p_value, v_ren, temperature, yeto):
#     V_ReN = v_ren
#     RP_values = [r["re_cr"] for r in recharge_rate]
#     RW_values = [r["re_ro"] for r in recharge_rate]
#     SumPW = sum(
#         [(RP_values[i] * land_use_area[i]["a5"] * 10 + RW_values[i] * land_use_area[i]["a6"] * 10) for i in range(36)])
#     FRD = SumPW
#     VSum_Ra = V_ReN + FRD
#     Sum_P = sum(p_value)
#     A = sum([area["a5"] + area["a6"] for area in land_use_area]) * 10  # Summing only numeric values
#     Rad = (VSum_Ra / A) * 0.001
#     Ro = Sum_P - Rad  # Calculate Yearly Runoff
#     answer = 1
#     RF = 0.9
#     if answer == 1:
#         Rad *= RF
#         Ro *= RF
#     Ratio_Ra_P = Rad / Sum_P
#     Ratio_Ro_P = Ro / Sum_P
#     tmean = [(data['t_max'] + data['t_min']) / 2 for data in temperature]
#     AI = Sum_P / sum(tmean)
#     PRa = 100 * Rad / Sum_P
#     PRo = 100 * Ro / Sum_P
#     if PRa > 40:
#         error = "The Recharge as a percentage of Rainfall is too high! Please Check the input Data"
#     else:
#         recharge_data = {
#             "Yearly Rainfall (mm)": Sum_P,
#             "Yearly Recharge (mm)": Rad,
#             "Yearly Runoff (mm)": Ro,
#             "Yearly Recharge as a percentage of Precipitation": PRa,
#             "Yearly Runoff as a percentage of Rainfall": PRo,
#             "Aridity Index (AI)": AI,
#             "YETO": yeto
#         }
#     return recharge_data
#

def calculate_wb_itself(catchment_area, land_use_area, kc_value, cn_value, p_value, temperature, eto_list1,
                        re_water_body, recharge_rate, outflow, rf, rf_option):
    VSumETp = 0
    VSumETa = 0
    VSumRojk = 0
    Sum_VrWb_2 = 0
    volume = []
    Sum_VRe = 0
    Sum_VRe_1 = 0
    total_volume = 0
    sum_temp = 0
    VrWb_list = []
    # Calculate 'a1' to 'a7' as a fraction of the catchment area
    for i in range(36):
        r = i
        row_data = land_use_area[i]

        # Check if Sum of A1…A7 of a row is equal to 100
        sum_row = sum(row_data.values())
        if sum_row != 100:
            error = 100 - sum_row
            if -5 <= error <= 0:
                row_data['a7'] -= error
            elif 0 < error <= 5:
                row_data['a7'] += error
            else:
                print(f"Sum of land-use components must be equal to 100, Line number {r + 1}")

        volume.append(round(catchment_area * p_value[i] * 1000, 2))
        total_volume += volume[i]

        last_rojk = 0
        for r in range(4):
            Etrk = round(kc_value[i]['kc_a{}'.format(r + 1)] * eto_list1[i] * 10, 1)
            VSumETp += Etrk * land_use_area[i][f'a{r + 1}']
            ETark = p_value[i] if p_value[i] <= Etrk else Etrk
            VSumETa += ETark * land_use_area[i][f'a{r + 1}']
            CNjk = cn_value[i]['cn{}'.format(r + 1)]
            Sjk = ((1000 / CNjk) - 10) * 10
            ajk = (p_value[i] - ETark - 0.2 * Sjk) ** 2
            bjk = (p_value[i] - ETark + 0.8 * Sjk)
            Qjk = round(ajk / bjk, 1)
            Rojk = Qjk
            VRojk = Rojk * land_use_area[i]['a{}'.format(r + 1)] * 1000
            VSumRojk += VRojk
            last_rojk = VRojk

            # Calculating Recharge (Re)
            QOutjk = ETark + Rojk
            if QOutjk < p_value[i]:
                Rejk = p_value[i] - QOutjk
            else:
                Rejk = 0
            Sum_VRe += Rejk

            Vre = Rejk * land_use_area[i]['a{}'.format(r + 1)] * 1000
            Sum_VRe_1 += Vre
            # print(f'Vre_{i}_{r}: {Vre}')

        VrWb = re_water_body[i] * land_use_area[i]['a6'] * 1000
        Sum_VrWb_2 += VrWb
        # print(f'VrWb_{i}_{r}: {VrWb}')

        t_mean = (temperature[i]['t_min'] + temperature[i]['t_max']) / 2
        sum_temp += t_mean

    V_ReN = Sum_VRe

    VSumRo = VSumRojk + (last_rojk * 5)
    # Sum up all recharges
    re_cr, re_ro, re_pa, re_other = [sum(entry[col] for entry in recharge_rate) for col in
                                     ['re_cr', 're_ro', 're_pa', 're_other']]
    Sum_Vre3 = re_cr + re_ro + re_pa + re_other
    out_dr, out_other = [sum(entry[col] for entry in outflow) for col in
                         ['out_dr', 'out_other']]

    Sum_Vre_out = out_dr + out_other
    sum_p_value = sum(p_value)
    VReNET = Sum_VRe_1 + Sum_VrWb_2 + Sum_Vre_out + Sum_Vre3
    Rad = (VReNET / catchment_area) * 0.001
    Ro = (VSumRo / catchment_area) * 0.001
    if rf_option == 1:
        Rad *= rf
        Ro *= rf
    recharge_percentage = 100 * (Rad / sum_p_value)
    aridity_index = sum_p_value / (sum_temp + 10)
    runoff_percentage = (Ro / sum_p_value) * 100
    # print(f'recharge_percentage: {recharge_percentage}')

    # print(f'Sum_VrWb_2: {Sum_VrWb_2}')

    if recharge_percentage / 100 > 40:  # Set your threshold here
        recharge_data = {
            'error': 'The Recharge as a percentage of Rainfall is too high! Please check the input data'
        }
    else:
        recharge_data = {
            "Yearly Rainfall (mm)": sum_p_value,
            "Yearly Recharge (mm)": round(Rad, 2),
            "Yearly Runoff (mm)": round(Ro, 2),
            "Yearly Recharge as a percentage of Precipitation": round(recharge_percentage, 2),
            "Yearly Runoff as percentage of Rainfall": round(runoff_percentage, 2),
            "Aridity Index (AI)": round(aridity_index, 2)
        }
    return recharge_data


def calculate_wb(catchment_area, land_use_area, kc_value, cn_value, p_value, temperature, eto_list1,
                 re_water_body, recharge_rate, outflow, rf, rf_option):
    response_data = {}
    v_sum_etp = 0
    v_sum_eta = 0
    v_sum_ro = 0
    v_sum_re = 0
    v_sum_rq = 0
    v_re_out = 0
    v_sum_re_wb = 0
    sum_pw = 0
    sumEtp = 0
    sumEta = 0
    v_sum_re_net = 0
    yearly_rainfall = 0

    v_sum_runoff = 0
    runoff_list = []
    for i in range(36):
        sum_pw += (((land_use_area[i]['a6'] / 100) * catchment_area) * 10) + (
                ((land_use_area[i]['a5'] / 100) * catchment_area) * 10)
        vr_wb = ((land_use_area[i]['a6'] / 100) * catchment_area) * re_water_body[i] * 1000

        v_sum_re_wb += vr_wb
        v_sum_rq += sum(recharge_rate[i].values())
        v_re_out += sum(outflow[i].values())
        sm_l = sum(land_use_area[i].values())
        er_l = 100 - sm_l
        if -5 <= er_l <= 0:
            land_use_area[i]['a7'] -= er_l
        elif 0 < er_l <= 5:
            land_use_area[i]['a7'] += er_l
        else:
            response_data['error'] = f'Sum of land-use components must be equal to 100, Line number {i + 1}'
            return response_data

    for i in range(36):
        for j in range(4):
            kc = kc_value[i]['kc_a{}'.format(j + 1)]
            p = p_value[i]
            c = cn_value[i]['cn{}'.format(j + 1)]
            land = (land_use_area[i]['a{}'.format(j + 1)] / 100) * catchment_area
            et_rk = eto_list1[0] * kc * 10
            sumEtp += et_rk

            v_sum_etp += (et_rk * 10) * land * catchment_area * 10
            if p < et_rk:
                eta_rk = p
            else:
                eta_rk = et_rk
            sumEta += eta_rk

            v_sum_eta += eta_rk * land * catchment_area * 10
            s_jk = ((1000 / c) - 10) * 10
            a_jk = (p - eta_rk - 0.2 * s_jk) ** 2
            b_jk = (p - eta_rk + 0.8 * s_jk)
            q_jk = a_jk / b_jk
            ro_jk = q_jk
            v_ro_jk = (ro_jk * 10) * (land * 10)
            v_sum_ro += v_ro_jk
            runoff = ro_jk * land * 1000
            runoff_list.append(round(runoff, 0))
            q_out_jk = eta_rk + ro_jk
            if q_out_jk < p:
                re_jk = p - q_out_jk
                v_re_jk = (re_jk * land) * 1000
            else:
                re_jk = 0
                v_re_jk = 0
            v_sum_re += v_re_jk

    yearly_rainfall = sum(p_value)
    v_ren = v_sum_re
    frd = sum_pw
    v_sum_ra = v_ren + frd
    v_sum_runoff = sum(runoff_list)

    rad = (v_sum_ra / catchment_area) * 0.001
    ro = (v_sum_runoff / catchment_area) * 0.001
    if rf_option == 1:
        rad *= rf
        ratio_ra_p = 100 * rad / sum(p_value)
        if rf != 0:
            ratio_ro_p = 100 * ro / (rf * sum(p_value))
        else:
            ratio_ro_p = 0  # or any appropriate value or handling for rf == 0
    else:
        ratio_ra_p = rad / sum(p_value)
        ratio_ro_p = ro / sum(p_value)

    ai = sum(p_value) / sumEtp
    pra = ratio_ra_p * 100
    pro = ratio_ro_p * 100
    net_recharge_volume = v_sum_re + v_sum_re_wb + v_sum_rq - v_re_out
    net_recharge_depth = (net_recharge_volume / catchment_area) * 0.001
    rainfall_percentage = 100 * (net_recharge_depth / sum(p_value))
    total_runoff = v_sum_runoff / (catchment_area * 1000)
    # aridity_index = net_recharge_volume / sum(p_value)

    response_data = {
        "Yearly Rainfall (mm)": round(yearly_rainfall, 2),
        "Yearly Recharge (mm)": round(net_recharge_depth, 2),
        "Yearly Runoff (mm)": round(total_runoff, 2),
        "rainfall_percentage (%)": round(rainfall_percentage, 2),

        # "Yearly Recharge as a percentage of Precipitation": pra,
        # "Yearly Runoff as percentage of Rainfall": pro,
        # "Aridity Index (AI)": ai
        # Include other data as needed
    }
    return response_data
