from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from estimation import constants
from estimation.models import EtoRsData, EtoShData
from estimation.utils import eto_methods


def process_land_use_data_with_cn_kc(land_use_area, kc_value, cn_value):
    if kc_value is None or cn_value is None:
        return {"error": "kc_value or cn_value is None"}
    for L, row in enumerate(land_use_area, 0):
        SM_L = sum(row.values())
        ER_L = 100 - SM_L
        if -5 <= ER_L <= 0:
            land_use_area[L - 1]["a7"] -= ER_L
        elif 0 < ER_L <= 5:
            land_use_area[L - 1]["a7"] += ER_L
        else:
            return {"error": f"Sum of land-use components must be equal to 100, Line number {L}, Stop"}
        KC_values = kc_value[L]
        CN_values = cn_value[L]
        for k, (CN, KC) in enumerate(zip(CN_values, KC_values), 0):
            land_use_area[L][f"CN{k}"] = CN
            land_use_area[L][f"KC{k}"] = KC
    return land_use_area


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
            YETO, eto_list = eto_methods.de_bruin_method(solar_radiation, temperature, latitude, elevation)
        else:
            return Response({'error': f"Method {eto_method} is not implemented yet"},
                            status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return YETO, eto_list


def calculate_volumes(land_use_area, kc_values, cn_values, p_values, temperature, yeto):
    v_sum_etp = 0
    v_sum_eta = 0
    v_sum_ro = 0
    sum_vre = 0

    for i in range(len(land_use_area)):
        a1, a2, a3, a4 = land_use_area[i]['a1'], land_use_area[i]['a2'], land_use_area[i]['a3'], land_use_area[i]['a4']
        total_area = a1 + a2 + a3 + a4
        for j in range(len(kc_values)):
            kc_value = kc_values[j]
            cn_value = cn_values[j]
            for k in range(1, 5):
                a_k = land_use_area[i][f'a{k}']
                pr = p_values[i]
                kc_a = kc_value[f'kc_a{k}']
                cn = cn_value[f'cn{k}']
                etrk = yeto * kc_a
                v_sum_etp += (etrk * 10) * (a_k * total_area * 10)
                if etrk <= pr:
                    etark = pr
                else:
                    s = (1000 / cn) - 10
                    ajk = (pr - etrk - 0.2 * s) ** 2
                    bjk = (pr - etrk + 0.8 * s)
                    etark = ajk / bjk
                v_sum_eta += (etark * 10) * (a_k * total_area * 10)

                p_j = p_values[i]
                tmax = temperature[k]['t_max']
                tmin = temperature[k]['t_min']
                et_ajk = (tmax + tmin) / 2
                cn_jk = cn_values[j][f'cn{k}']
                s_jk = (1000 / cn_jk) - 10
                ajk = (p_j - et_ajk - 0.2 * s_jk) ** 2
                bjk = (p_j - et_ajk + 0.8 * s_jk)
                q_jk = ajk / bjk
                ro_jk = q_jk
                v_sum_ro += (ro_jk * 10) * (land_use_area[i][f'a{k}'] * total_area * 10)

    for i in range(len(p_values)):
        for k in range(1, 5):
            a_jk = land_use_area[i][f'a{k}']
            et_ajk = 10
            r0_jk = 5
            q_out_jk = et_ajk + r0_jk
            p_k = p_values[i]
            if q_out_jk < p_k:
                re_jk = p_k - q_out_jk
                v_re_jk = re_jk * 10 * a_jk * 10
            else:
                v_re_jk = 0
            sum_vre += v_re_jk

    v_ren = sum_vre
    return v_ren


def calculate_recharge(land_use_area, recharge_rate, p_value, v_ren, temperature, yeto):
    V_ReN = v_ren
    RP_values = [r["re_previous"] for r in recharge_rate]
    RW_values = [r["re_water_body"] for r in recharge_rate]
    SumPW = sum(
        [(RP_values[i] * land_use_area[i]["a5"] * 10 + RW_values[i] * land_use_area[i]["a6"] * 10) for i in range(36)])
    FRD = SumPW
    VSum_Ra = V_ReN + FRD
    Sum_P = sum(p_value)
    A = sum([area["a5"] + area["a6"] for area in land_use_area]) * 10  # Summing only numeric values
    Rad = (VSum_Ra / A) * 0.001
    Ro = Sum_P - Rad  # Calculate Yearly Runoff
    Answer = 1
    RF = 0.9
    if Answer == 1:
        Rad *= RF
        Ro *= RF
    Ratio_Ra_P = Rad / Sum_P
    Ratio_Ro_P = Ro / Sum_P
    tmean = [(data['t_max'] + data['t_min']) / 2 for data in temperature]
    AI = Sum_P / sum(tmean)
    PRa = 100 * Rad / Sum_P
    PRo = 100 * Ro / Sum_P
    if PRa > 40:
        error = "The Recharge as a percentage of Rainfall is too high! Please Check the input Data"
    else:
        recharge_data = {
            "Yearly Rainfall (mm)": Sum_P,
            "Yearly Recharge (mm)": Rad,
            "Yearly Runoff (mm)": Ro,
            "Yearly Recharge as a percentage of Precipitation": PRa,
            "Yearly Runoff as a percentage of Rainfall": PRo,
            "Aridity Index (AI)": AI,
            "YETO": yeto
        }
    return recharge_data
