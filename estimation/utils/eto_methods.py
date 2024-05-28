import math
from rest_framework import serializers
import pandas as pd


def eto_method_validation(data):
    eto_method = data.get('eto_method')
    land_use_area = data.get('land_use_area')
    kc_value = data.get('kc_value')
    cn_value = data.get('cn_value')
    if land_use_area is not None and len(land_use_area) != 36:
        raise serializers.ValidationError({"error": "The length of land_use_area must be 36"})
    elif kc_value is not None and len(kc_value) != 36:
        raise ValueError("Length of kc_value is not equal to 36.")
    elif cn_value is not None and len(cn_value) != 36:
        raise serializers.ValidationError({"error": "The length of cn_value must be 36"})
    required_fields_map = {
        1: ['latitude', 'elevation', 'eto_rs_data', 'temperature'],
        2: ['latitude', 'elevation', 'eto_sh_data', 'temperature'],
        3: ['latitude', 'elevation', 'eto_sh_data', 'temperature'],
        4: ['latitude', 'c_value', 'temperature'],
        5: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        6: ["latitude", "temperature"],
        7: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        8: ["solar_radiation", "rh_value", "temperature"],
        9: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        10: ["c_value", "solar_radiation", "temperature"],
        11: ["c_value", 'solar_radiation', 'temperature'],
        12: ["latitude", "solar_radiation", 'temperature', 'elevation']
        #     TODO: Need to add required field.
    }

    required_fields = required_fields_map.get(eto_method, [])
    missing_fields = [field for field in required_fields if data.get(field) is None]

    if missing_fields:
        missing_fields_str = ', '.join(missing_fields)
        raise serializers.ValidationError(
            f"{missing_fields_str.capitalize()} {'and' if len(missing_fields) > 1 else ''} {'are' if len(missing_fields) > 1 else 'is'} required for eto_method {eto_method}"
        )


def fao_combined_pm_method(latitude, elevation, eto_rs_data, temperature):
    """
    Calculate Yearly ET0 using the FAO Combined P-M method with Rs option 1.1.

    Args:
    - latitude (float): Latitude in decimal form.
    - elevation (float): Elevation in meters.
    - climatic_data (list): List containing climatic input data for 36 periods.
        Each period should have the format: (RH, WS, SR).

    Returns:
    - YET0 (float): Yearly ET0 value.
    """
    # Constants
    # data = []
    Lambda = 2.4536
    z = elevation
    # Initialize variables
    SumET0 = 0
    Lrad = round(latitude * math.pi / 180, 2)

    daily_eto = []
    for r in range(36):
        RH_t = eto_rs_data[r]['RH_t']
        WS_t = eto_rs_data[r]['WS_t']
        SR_t = eto_rs_data[r]['SR_t']
        Tmax_t = temperature[r]['t_max']
        Tmin_t = temperature[r]['t_min']

        # Calculation of mean temperature
        Tmean_t = (Tmax_t + Tmin_t) / 2
        p = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.253
        gamma = 0.00163 * p / Lambda
        # Calculation of Ra (Extraterrestrial Radiation)
        J_t = (10 * (r + 1)) - 5  # r starts from 0, hence +1
        del_t = 0.409 * math.sin((0.0172 * J_t - 1.39))
        dr_t = 1 + 0.033 * math.cos((0.0172 * J_t))
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * ((ws_t * math.sin(math.radians(latitude * 22 / (180 * 7))) * math.sin(del_t)) + (
                math.cos(math.radians(latitude * 22 / (180 * 7))) * math.cos(del_t) * math.sin(ws_t)))

        # Calculation of es, ea, delta
        es_Tmax_t = 0.6108 * math.exp((17.27 * Tmax_t) / (Tmax_t + 237.3))
        es_Tmin_t = 0.6108 * math.exp((17.27 * Tmin_t) / (Tmin_t + 237.3))
        es_t = (es_Tmax_t + es_Tmin_t) / 2
        ea_t = (RH_t / 100) * es_t
        Delta_t = 4098 * ea_t / ((Tmean_t + 237.3) ** 2)

        # Calculation of Rns, Rnl, Rn

        Rns_t = 0.77 * SR_t
        Rnl_t = (4.903 * 10 ** -9) * 0.5 * (
                ((Tmax_t + 273.16) ** 4 + (Tmin_t + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea_t)) * (
                1.136 * SR_t / (0.75 * Ra_t)) - 0.07)

        # rnl_t= (4.903 * 10**-9) * ((((Tmax_t + 273.16)**4) + (Tmin_t + 273.16)**4) / 2) * (.34-0.139 * math.sqrt(ea_t)) * ((1.350 * SR_t / (0.75 * Z)) + AD2)
        Rn_t = Rns_t - Rnl_t
        R_t = 0.408 * Delta_t * Rn_t

        # Calculation of A (Aerodynamic term)
        A_t = gamma * 900 * WS_t * (es_t - ea_t) / (Tmean_t + 273)

        # Calculation of D (Denominator part)
        D_t = Delta_t + gamma * (1 + 0.34 * WS_t)

        # Calculation of ET0 for the current period
        ET0_t = (R_t + A_t) / D_t

        # Accumulate ET0 for SumET0
        SumET0 += ET0_t * 10  # Considering 10-day periods
        # data.append([
        #     round(RH_t, 2), round(WS_t, 2), round(SR_t, 2), round(Tmax_t, 2), round(Tmin_t, 2), round(Tmean_t, 2),
        #     round(p, 2), round(gamma, 2), round(J_t, 2), round(del_t, 2), round(dr_t, 2), round(ws_t, 2),
        #     round(Ra_t, 2),
        #     round(es_Tmax_t, 2), round(es_Tmin_t, 2), round(es_t, 2), round(ea_t, 2), round(Delta_t, 2),
        #     round(Rns_t, 2),
        #     round(Rnl_t, 2), round(Rn_t, 2), round(R_t, 2), round(A_t, 2), round(D_t, 2), round(ET0_t, 2)
        # ])
    # columns = ["RH_t", "WS_t", "SR_t", "Tmax_t", "Tmin_t", "Tmean_t", "p", "gamma", "J_t", "del_t",
    #            "dr_t", "ws_t", "Ra_t", "es_Tmax_t", "es_Tmin_t", "es_t", "ea_t", "Delta_t", "Rns_t", "Rnl_t",
    #            "Rn_t", "R_t", "A_t", "D_t", "ET0_t"]

    # df = pd.DataFrame(data, columns=columns)
    # df.to_excel("FAO_Combined_PM_Method_Full_OUTPUT.xlsx", index=False)
    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_t * 5)  # Multiply by 5 as there are 36 periods

    return YET0


def pm_method_sh(latitude, elevation, eto_sh_data, temperature):
    Lambda = 2.4536
    SumET0 = 0
    z = elevation
    Lrad = latitude * math.pi / 180
    # data = []

    for r in range(0, len(eto_sh_data)):
        Tmax_t = temperature[r]['t_max']
        Tmin_t = temperature[r]['t_min']
        RH_t = eto_sh_data[r]['RH_t']
        WS_t = eto_sh_data[r]['WS_t']
        SH_t = eto_sh_data[r]['SH_t']
        Tmean_t = (Tmax_t + Tmin_t) / 2
        P = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.253
        gamma = round(0.00163 * P / Lambda, 2)
        # Calculation of Ra
        J_t = 10 * (r + 1) - 5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * ((ws_t * math.sin(Lrad) * math.sin(del_t)) + (
                math.cos(Lrad) * math.cos(del_t) * math.sin(ws_t)))
        N_t = (24 * ws_t) / 3.1416
        Rs_t = (0.25 + 0.50 * SH_t / N_t) * Ra_t
        # Calculation of es, ea, delta
        es_Tmax_t = 0.6108 * math.exp((17.27 * Tmax_t) / (Tmax_t + 237.3))
        es_Tmin_t = 0.6108 * math.exp((17.27 * Tmin_t) / (Tmin_t + 237.3))
        es_t = (es_Tmax_t + es_Tmin_t) / 2
        ea_t = (RH_t / 100) * es_t
        Delta_t = 4098 * ea_t / ((Tmean_t + 273.3) ** 2)
        # Calculation of Rns, Rso, Rnl, Rn
        Rns_t = 0.77 * Rs_t
        Rnl_t = (4.903 * 10 ** -9) * (
                (((Tmax_t + 273.16) ** 4 + (Tmin_t + 273.16) ** 4) / 2) *
                (0.34 - 0.14 * math.sqrt(ea_t)) *
                ((1.350 * Rs_t / (0.75 * Ra_t)) + (-0.35))
        )
        Rn_t = Rns_t - Rnl_t
        R_t = 0.408 * Delta_t * (Rns_t - Rnl_t)
        # Calculation of A (Aerodynamic term)
        A_t = gamma * 900 * WS_t * (es_t - ea_t) / (Tmean_t + 273)
        # Calculation of D (Denominator part)
        D_t = Delta_t + gamma * (1 + 0.34 * WS_t)
        # Calculation of ET0 for the current period
        ET0_t = (R_t + A_t) / D_t
        SumET0 += ET0_t * 10  # Considering 10-day periods

        # print(
        #     f'RH_t: {round(RH_t, 2)}, WS_t: {round(WS_t, 2)}, SH_t: {round(SH_t, 2)}, Tmax_t: {round(Tmax_t, 2)}, '
        #     f'Tmin_t: {round(Tmin_t, 2)}, Tmean_t: {round(Tmean_t, 2)}, p: {round(P, 2)}, gamma: {round(gamma, 2)}, '
        #     f'J_t: {round(J_t, 2)}, del_t: {round(del_t, 2)}, dr_t: {round(dr_t, 2)}, ws_t: {round(ws_t, 2)}, '
        #     f'Ra_t: {round(Ra_t, 2)}, es_Tmax_t: {round(es_Tmax_t, 2)}, es_Tmin_t: {round(es_Tmin_t, 2)}, '
        #     f'es_t: {round(es_t, 2)}, ea_t: {round(ea_t, 2)}, Delta_t: {round(Delta_t, 2)}, Rns_t: {round(Rns_t, 2)}, '
        #     f'Rnl_t: {round(Rnl_t, 2)}, Rn_t: {round(Rn_t, 2)}, R_t: {round(R_t, 2)}, A_t: {round(A_t, 2)}, '
        #     f'D_t: {round(D_t, 2)}, ET0_t: {round(ET0_t, 2)}'
        # )
        # print(f'Delta_t: {Delta_t:.2f},A_t: {A_t:.2f},ET0_t: {ET0_t:.2f},D: {D_t:.2f}, Rs_t: {Rs_t:.2f},Ra_t:{Ra_t:.2f}')
        # print(
        #     f'Tmax: {round(Tmax_t, 2)}\tTmin: {round(Tmin_t, 2)}\tRHmean: {round(RH_t, 2)}\tWind(m/s): {round(WS_t, 2)}\t'
        #     f'SH (hr): {round(SH_t, 2)}\tET0_P-M: {round(ET0_t, 2)}\tJ-t: {round(J_t, 2)}\tdel: {round(del_t, 1)}\tdr: {round(dr_t, 2)}\t'
        #     f'ws: {round(ws_t, 2)}\tRa: {round(Ra_t, 2)}\tN: {round(N_t, 2)}\tRs: {round(Rs_t, 2)}\tTmean: {round(Tmean_t, 2)}\t'
        #     f'es(Tmax): {round(es_Tmax_t, 2)}\tes(Tmin): {round(es_Tmin_t, 2)}\tes: {round(es_t, 2)}\tea: {round(ea_t, 2)}\t'
        #     f'es - ea: {round(es_t - ea_t, 2)}\t∆: {round(Delta_t, 2)}\tRns: {round(Rns_t, 2)}\tRnl: {round(Rnl_t, 2)}\t'
        #     f'Rn: {round(Rn_t, 2)}\tRad.term: {round(R_t, 2)}\tP-atm.: {round(P, 2)}\tlambda: {round(Lambda, 4)}\t'
        #     f'gamma: {round(gamma, 4)}\tAeroterm: {round(A_t, 2)}\tD (mm/d): {round(D_t, 2)}\tEto: {round(ET0_t, 2)}'
        # )
        # result = 4098 * ea_t / ((Tmean_t + 273.3) ** 2)
        # print(f'4098 * {round(ea_t, 2)} / (({Tmean_t} + 237.3) ** 2) = {round(result,2)}')

        # data.append({
        #     'Tmax': round(Tmax_t, 2),
        #     'Tmin': round(Tmin_t, 2),
        #     'RHmean': round(RH_t, 2),
        #     'Wind(m/s)': round(WS_t, 2),
        #     'SH (hr)': round(SH_t, 2),
        #     'ET0_P-M': round(ET0_t, 2),
        #     'J-t': round(J_t, 2),
        #     'del': round(del_t, 1),
        #     'dr': round(dr_t, 2),
        #     'ws': round(ws_t, 2),
        #     'Ra': round(Ra_t, 2),
        #     'N': round(N_t, 2),
        #     'Rs': round(Rs_t, 2),
        #     'Tmean': round(Tmean_t, 2),
        #     'es(Tmax)': round(es_Tmax_t, 2),
        #     'es(Tmin)': round(es_Tmin_t, 2),
        #     'es': round(es_t, 2),
        #     'ea': round(ea_t, 2),
        #     'es - ea': round(es_t - ea_t, 2),
        #     '∆': round(Delta_t, 2),
        #     'Rns': round(Rns_t, 2),
        #     'Rnl': round(Rnl_t, 2),
        #     'Rn': round(Rn_t, 2),
        #     'Rad.term': round(R_t, 2),
        #     'P-atm.': round(P, 2),
        #     'lambda': round(Lambda, 4),
        #     'gamma': round(gamma, 4),
        #     'Aeroterm': round(A_t, 2),
        #     'D (mm/d)': round(D_t, 2),
        #     'Eto': round(ET0_t, 2)
        # })

    # Calculation of Yearly ET0
    # df = pd.DataFrame(data)
    # df.to_excel('pm_method_sh_output.xlsx', index=False)
    YET0 = SumET0 + (ET0_t * 5)  # Multiply by 5 as there are 36 periods
    return YET0


def pm_method_no_rs_sh(latitude, elevation, eto_sh_data, temperature):
    Lambda = 2.4536
    SumET0 = 0
    Lrad = latitude * math.pi / 180
    Z = elevation
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    gamma = round(0.00163 * P / Lambda, 2)
    data = []
    for t in range(36):
        RH_t = eto_sh_data[t]['RH_t']
        WS_t = eto_sh_data[t]['WS_t']
        Tmax_t = temperature[t]['t_max']
        Tmin_t = temperature[t]['t_min']
        Tmean_t = (Tmax_t + Tmin_t) / 2
        J_t = (10 * (t + 1) - 5) + 0.5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * (
                (ws_t * math.sin(Lrad) * math.sin(del_t)) + (math.cos(Lrad) * math.cos(del_t) * math.sin(ws_t)))
        N_t = 7.64 * ws_t

        Rs_t = 0.16 * (math.sqrt(Tmax_t - Tmin_t)) * Ra_t
        # Calculation of es, ea, delta
        es_Tmax_t = 0.6108 * math.exp((17.27 * Tmax_t) / (Tmax_t + 237.3))
        es_Tmin_t = 0.6108 * math.exp((17.27 * Tmin_t) / (Tmin_t + 237.3))
        es_t = (es_Tmax_t + es_Tmin_t) / 2
        ea_t = (RH_t / 100) * es_t
        Delta_t = 4098 * ea_t / (Tmean_t + 237.3) ** 2
        # print(
        #     f'Tmax_t: {Tmax_t}, Tmin_t: {Tmin_t}, Tmean_t: {Tmean_t},RH_t: {RH_t}, WS_t: {WS_t}, es_Tmax_t: {es_Tmax_t}, es_Tmin_t: {es_Tmin_t}, es_t: {es_t}, ea_t:  {ea_t}, Delta_t: {Delta_t}')
        # print(
        #     f'es_Tmax_t: {round(es_Tmax_t, 2)}, es_Tmin_t: {round(es_Tmin_t, 2)}, es_t: {round(es_t, 2)}, ea_t: {round(ea_t, 2)},P-atm: {round(P, 2)},lambda: {round(Lambda, 2)},gamma: {round(gamma, 2)}, Delta_t: {round(Delta_t, 2)}')

        # Calculation of Rns, Rnl, Rn

        Rns_t = (1 - 0.23) * Rs_t
        Rnl_t = (4.903 * 10 ** -9) * (
                (((Tmax_t + 273.16) ** 4 + (Tmin_t + 273.16) ** 4) / 2) *
                (0.34 - 0.14 * math.sqrt(ea_t)) *
                ((1.350 * Rs_t / (0.75 * Ra_t)) + (-0.35))
        )
        Rn_t = Rns_t - Rnl_t
        R_t = 0.408 * Delta_t * (Rn_t)
        # Calculation of A
        A_t = gamma * 900 * WS_t * (es_t - ea_t) / (Tmean_t + 273)
        # Calculation of D
        D_t = Delta_t + gamma * (1 + 0.34 * WS_t)
        # Calculation of ET0 for the current period
        ET0_t = (R_t + A_t) / D_t
        print(
            f'del_t:{round(del_t, 1)}, ws_t:{round(ws_t, 2)},dr_t:{round(dr_t, 2)},Ra_t:{round(Ra_t, 2)},Rs_t:{round(Rs_t, 2)},Rns_t: {round(Rns_t, 2)},Rnl_t: {round(Rnl_t, 2)},Rn_t: {round(Rn_t, 2)},R_t:{round(R_t, 2)}, D_t: {round(D_t, 3)}, ET0_t:{round(ET0_t, 2)}, J-t: {J_t}')

        # Accumulate ET0 for SumET0
        SumET0 += ET0_t * 10  # Considering 10-day periods
        data.append({
            'Tmax': round(Tmax_t, 2),
            'Tmin': round(Tmin_t, 2),
            'RHmean': round(RH_t, 2),
            'Wind(m/s)': round(WS_t, 2),
            'ET0_P-M': round(ET0_t, 2),
            'J-t': round(J_t, 2),
            'del': round(del_t, 1),
            'dr': round(dr_t, 2),
            'ws': round(ws_t, 2),
            'Ra': round(Ra_t, 2),
            'N': round(N_t, 2),
            'Rs': round(Rs_t, 2),
            'Tmean': round(Tmean_t, 2),
            'es(Tmax)': round(es_Tmax_t, 2),
            'es(Tmin)': round(es_Tmin_t, 2),
            'es': round(es_t, 2),
            'ea': round(ea_t, 2),
            'es - ea': round(es_t - ea_t, 2),
            '∆': round(Delta_t, 2),
            'Rns': round(Rns_t, 2),
            'Rnl': round(Rnl_t, 2),
            'Rn': round(Rn_t, 2),
            'Rad.term': round(R_t, 2),
            'P-atm.': round(P, 2),
            'lambda': round(Lambda, 4),
            'gamma': round(gamma, 4),
            'Aeroterm': round(A_t, 2),
            'D (mm/d)': round(D_t, 2),
            'Eto': round(ET0_t, 2)
        })

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_t * 5)  # Multiply by 5 as there are 36 periods
    df = pd.DataFrame(data)
    # df.to_excel('pm_method_no_rs_sh_output.xlsx', index=False)
    return YET0


def fao_blaney_criddle_method(latitude, c_values, temperature, p_value):
    # TODO: Check list pass.
    """
    Calculate reference evapotranspiration (ETO) using the FAO Blaney-Criddle method.

    Args:
        latitude (float): Latitude of the location in decimal degrees.
        c_values (list of float): List of C values for each time period.
        t_mean_value (list of float): List of mean temperature values for each time period.
        p_value (list of float): List of p values for each time period.

    Returns:
        float: Calculated reference evapotranspiration (ETO) value.
    """
    # Convert latitude to radians
    Lrad = latitude * math.pi / 180

    # Initialize variables
    sumN = 0
    ET0_values = []

    # Create DataFrame to store intermediate values

    # Calculate yearly N (YN) and p values
    YN = 0
    csv_data = []
    for i in range(36):
        T_mean = (temperature[i]['t_max'] + temperature[i]['t_min']) / 2
        J_t = 10 * (i + 1) - 5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        N_t = 7.64 * ws_t
        sumN += N_t
        YN = N_t * 10
        #
        # print(
        #     f'Lrad: {Lrad}, del_t: {round(del_t, 2)},dr_t: {round(dr_t, 2)},ws_t: {round(ws_t, 2)}, N_t: {round(N_t, 2)},N_t*10: {round(N_t * 10, 2)}')

        # Calculate p values
        p_t = p_value[i]

        # Calculate ET0 values
        c_t = c_values[i]
        ET0_t = c_t * p_t * (0.46 * T_mean + 8)
        print(f'ET0_calculation: {round(ET0_t, 2)}')
        ET0_values.append(ET0_t)
    # Calculate yearly ET0 (YET0)
    SumET0 = sum(ET0_values)
    YET0 = SumET0
    return YET0


def makkink_method(latitude, elevation, solar_radiation, temperature):
    data = []
    # Constants
    Lambda = 2.4536
    Lrad = latitude * math.pi / 180
    z = elevation
    P = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    gamma = 0.00163 * P / Lambda
    sum_eto = 0

    # Calculate delta and Tmean for each time step and simultaneously calculate ET0
    for i in range(36):
        Rs = solar_radiation[i]
        Tmax = temperature[i]['t_max']
        Tmin = temperature[i]['t_min']
        Tmean = (Tmax + Tmin) / 2

        # Calculate delta
        ea = 0.6108 * math.exp((17.27 * Tmean) / (Tmean + 237.2))
        delta = 4098 * ea / (Tmean + 237.3) ** 2

        # Calculate ET0 for the current time step
        ET0 = ((0.61 * Rs * delta) / ((delta + gamma) * Lambda)) - 0.12
        sum_eto += ET0
        data.append([
            round(Tmean, 2), round(P, 2), round(gamma, 2), round(ea, 2), round(delta, 2), round(ET0, 2)
        ])
    columns = ["Tmean", "P", "Gamma", "ea", "delta", "eto"]

    df = pd.DataFrame(data, columns=columns)
    # df.to_excel("makkink_method_output.xlsx", index=False)
    Yeto = sum_eto
    return Yeto


def hargreaves_method(latitude, temperature):
    """
    Calculate ET0 using Hargreaves method and generate an Excel file with the data.

    Args:
        latitude (float): Latitude in degrees.
        temperature (list): List of dictionaries with 't_max' and 't_min' values for each day.

    Returns:
        float: Yearly ET0 value.

    Raises:
        ValueError: If the length of 'temperature' is not 36.
    """
    if len(temperature) != 36:
        raise ValueError("Temperature data should be provided for 36 days.")

    # Convert latitude to radians
    Lrad = latitude * math.pi / 180
    sum_et0 = 0
    lambda_value = 2.4536

    print(f'Table 4- HG .xlsx')
    for t in range(36):
        # Extract temperature data for the current day
        tmax = temperature[t]['t_max']
        tmin = temperature[t]['t_min']
        tmean = (tmax + tmin) / 2

        # Calculate J, del, dr, ws
        j = (10 * (t + 1)) - 5
        delta = 0.409 * math.sin(0.0172 * j - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * j)
        ws = round(math.acos(-math.tan(Lrad) * math.tan(delta)), 2)

        # Calculate Ra
        ra = 37.6 * dr * (
                (ws * math.sin(Lrad) * math.sin(delta)) + (math.cos(Lrad) * math.cos(delta) * math.sin(ws)))
        # Calculate ET0
        et0 = (0.0023 * ra / lambda_value) * (tmean + 17.8) * math.sqrt((tmax - tmin))
        sum_et0 += et0
        print(f'Eto: {round(et0, 2)}')

    yet0 = sum_et0
    return yet0


def hansen_method(latitude, elevation, solar_radiation, temperature):
    # TODO: Check list pass.
    """
    Calculate ET0 using Hansen (1984) method.

    Args:
    - temperature (list): List of dictionaries containing maximum and minimum temperature data for 36 days.
    - rs_value (list): List of Rs values for 36 days.
    - latitude (float): Latitude in degrees.
    - elevation (float): Elevation in meters.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    if len(temperature) != 36 or len(solar_radiation) != 36:
        raise ValueError("Temperature data and Rs values should be provided for 36 days.")

    # Convert latitude to radians
    phi = math.radians(latitude)

    # Initialize sumET0
    sum_et0 = 0
    data = []

    # Constants
    lambda_value = 2.4536

    # Calculate P
    z = elevation
    P = 101.3 * math.pow(((293 - 0.0065 * z) / 293), 5.26)

    # Calculate gamma
    gamma = 0.00163 * P / lambda_value
    print(f'Table 5- Hansen .xlsx')
    for k in range(36):
        # Calculate Tmean
        t_max = temperature[k]['t_max']
        t_min = temperature[k]['t_min']
        t_mean = (t_max + t_min) / 2

        # Calculate delta
        ea = 0.6108 * math.exp((17.27 * t_mean) / (t_mean + 237.2))
        delta = 4098 * ea / math.pow((t_mean + 237.3), 2)

        # Calculate ET0
        et0 = (0.7 * solar_radiation[k] * delta) / ((delta + gamma) * lambda_value)

        print(f'et0___{k}: {et0:.2f} m')

        # Add ET0 to sumET0
        sum_et0 += et0
        data.append([
            round(t_mean, 2), round(P, 2), round(gamma, 2), round(ea, 2), round(delta, 2), round(et0, 2)
        ])
    columns = ["Tmean", "P", "Gamma", "ea", "delta", "eto"]

    df = pd.DataFrame(data, columns=columns)
    # df.to_excel("hansen_method_output.xlsx", index=False)
    Yeto = sum_et0
    return Yeto


def turc_method(solar_radiation, rh_value, temperature):
    # TODO: Check list pass.
    """
    Calculate ET0 using Turc method.

    Args:
    - temperature (list): List of dictionaries containing Tmax and Tmin for 36 days.
    - rs_data (list): List of Rs values for 36 days.
    - rh_data (list): List of RH values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """

    if len(temperature) != 36 or len(solar_radiation) != 36 or len(rh_value) != 36:
        raise ValueError("Data should be provided for all 36 days.")

    # Initialize sumET0
    sum_et0 = 0
    data = []
    for t in range(36):
        Tmax = temperature[t]["t_max"]
        Tmin = temperature[t]["t_min"]
        tmean = (Tmax + Tmin) / 2
        rs = solar_radiation[t]
        rh = rh_value[t]
        if rh < 50:
            aT = 1 + (50 - rh) / 70
        else:
            aT = 1
        et0 = (aT * 0.013 * (tmean / (tmean + 15))) * (23.8856 * rs + 50)
        sum_et0 += et0
        data.append([
            round(Tmax, 1), round(Tmin, 1), round(tmean, 1), round(rs, 1), round(aT, 1), round(et0, 1)
        ])
    yet0 = sum_et0
    columns = ["Tmax", "Tmin", "tmean", "Rs", "aT", "ETO"]
    df = pd.DataFrame(data, columns=columns)
    # df.to_excel("turc_method_output.xlsx", index=False)
    return yet0


def priestley_taylor_method(latitude, elevation, solar_radiation, temperature):
    # TODO: Check list pass.
    """
    Calculate ET0 using the Priestley-Taylor method.

    Args:
    - latitude (float): Latitude in degrees.
    - elevation (float): Elevation in meters.
    - temperature (list): List of dictionaries containing Tmax and Tmin for 36 days.
    - rs_data (list): List of Rs values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    # Convert latitude to radians
    Lrad = latitude * math.pi / 180

    # Constants
    lambda_value = 2.4536

    # Calculate gama
    z = elevation
    p = 101.3 * (((293 - 0.0065 * z) / 293) ** 5.26)
    gama = 0.00163 * p / lambda_value
    sum_et0 = 0
    data = []
    for i in range(36):
        # Calculate Tmean
        tmax = temperature[i]["t_max"]
        tmin = temperature[i]["t_min"]
        tmean = (tmax + tmin) / 2

        # Calculate Delta
        ea = 0.6108 * math.exp((17.27 * tmean) / (tmean + 237.2))
        delta = (4098 * ea) / ((tmean + 237.3) ** 2)

        # Calculate Ra
        j = (10 * (i + 1)) - 5
        delta_rad = 0.409 * math.sin(0.0172 * j - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * j)
        ws = math.acos(-math.tan(Lrad) * math.tan(delta_rad))
        ra = 37.6 * dr * (
                (ws * math.sin(Lrad) * math.sin(delta_rad)) + (math.cos(Lrad) * math.cos(delta_rad) * math.sin(ws))
        )

        # Calculate Rn
        rs = solar_radiation[i]
        rns = 0.77 * rs
        rnl = (4.903 * (10 ** -9)) * 0.5 * (
                ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea)) * (1.35 * rs) / (
                0.75 * ra - 0.35))
        rn = rns - rnl

        # Calculate ET0
        et0 = 1.26 * (delta / (delta + gama)) * ((rn - 0) / lambda_value)
        # Add ET0 to sumET0
        sum_et0 += et0
        data.append([
            round(tmax, 2), round(tmin, 2), round(rs, 2), round(tmean, 2),
            round(p, 1), round(gama, 2), round(ea, 2), round(delta, 2),
            round(j, 2), round(Lrad, 2), round(delta_rad, 2), round(dr, 2),
            round(ws, 2), round(ra, 1), round(rns, 2), round(rnl, 2),
            round(rn, 2), round(et0, 2)
        ])

    yet0 = sum_et0
    columns = [
        "Tmax", "Tmin", "Rs", "Tmean", "P", "Gamma", "Ea", "Delta",
        "J", "Lrad", "Delta_rad", "Dr", "Ws", "Ra",
        "Rns", "Rnl", "Rn", "ET0"
    ]
    df = pd.DataFrame(data, columns=columns)
    # df.to_excel('priestley_taylor_method_output.xlsx', index=False)
    return yet0


def jensen_haise_method(c_value, solar_radiation, temperature):
    # TODO: Check list pass.
    """
    Calculate ET0 using Jensen-Haise method.

    Args:
    - temperature (list): List of dictionaries containing Tmean for 36 days.
    - rs_values (list): List of Rs values for 36 days.
    - c_values (list): List of C values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    if len(temperature) != 36 or len(solar_radiation) != 36 or len(c_value) != 36:
        raise ValueError("Temperature, Rs, and C data should be provided for all 36 days.")

    # Constants
    lambda_value = 2.4536
    data = []

    sum_et0 = 0
    print('Table 8  -Jensen-Haise.xlsx')
    print('-' * 30)
    for i in range(36):
        # Calculate Tmean
        tmean = (temperature[i]["t_max"] + temperature[i]["t_min"]) / 2
        # Calculate ET0
        et0 = c_value[i] * (solar_radiation[i] * (0.025 * tmean + 0.08) / lambda_value)
        print(f'ET0__{i}: {et0:.2f} m')
        # Add ET0 to sumET0
        sum_et0 += et0
        data.append([round(solar_radiation[i], 2), round(c_value[i], 2), round(et0, 2)])
        print(f'solar_radiation: {solar_radiation[i]}, c_value: {c_value[i]}, et0: {round(et0, 2)}')

    columns = [
        'Rs(MJ/m^2/d)', 'C', 'ETO (mm/d)'
    ]
    df = pd.DataFrame(data=data, columns=columns)
    # df.to_excel('jensen_haise_method_output.xlsx', index=False)
    # Calculate Yearly ET0
    yet0 = sum_et0

    return yet0

    # Calculate Yearly ET0


def abtew_method(c_value, solar_radiation):
    # TODO: Check list pass.
    """
    Calculate potential evapotranspiration (PET) using Abtew method.

    Args:
    - rs_values (list): List of Rs values for 36 days.
    - c_values (list): List of C values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    # Constants
    ki = 0.53
    lambda_value = 2.4536
    sum_et0 = 0
    data = []
    for j in range(36):
        # Calculate ET0
        rs_value = solar_radiation[j]
        c = c_value[j]
        et0 = c * ki * rs_value / lambda_value
        sum_et0 += et0
        data.append([round(solar_radiation[j], 2), round(c_value[j], 2), round(et0, 2)])
        print(f'solar_radiation: {rs_value}, c_value: {c_value[j]}, et0: {round(et0, 2)}')

    columns = [
        'Rs(MJ/m^2/d)', 'C', 'ETO (mm/d)'
    ]
    df = pd.DataFrame(data=data, columns=columns)
    # df.to_excel('abtew_method_11_output.xlsx', index=False)
    # Calculate Yearly ET0
    yet0 = sum_et0

    return yet0


def de_bruin_method(solar_radiation, temperature, latitude, elevation):
    # Constants
    Lambda = 2.4536  # Latent heat of vaporization (MJ/kg)
    C = 0.65  # Given constant

    # Convert latitude to radians
    # Lrad = latitude * math.pi / 180

    # Calculate pressure
    P = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26

    # Calculate gamma
    Gama = 0.00163 * P / Lambda
    # Initialize ET0 sum
    ET0sum = 0
    data = []
    for i in range(36):
        Tmax = temperature[i]['t_max']
        Tmin = temperature[i]['t_min']
        Tmean = (Tmax + Tmin) / 2
        ea = 0.6108 * math.exp((17.27 * Tmean) / (Tmean + 237.2))
        Delta = 4098 * ea / ((Tmean + 237.2) ** 2)
        Rs_val = solar_radiation[i]
        ET0 = (C * Rs_val / Lambda) * (Delta / (Delta + Gama))
        # ET0sum += ET0 * 10
        ET0sum += ET0
        data.append([round(P, 2), round(Gama, 2), round(ea, 2), round(Delta, 2), round(ET0, 2)])

    columns = ['P', 'Gama', 'ETA', 'Delta', 'Eto']
    df = pd.DataFrame(data, columns=columns)
    # df.to_excel('de_bruin_output.xlsx', index=False)
    # if len(solar_radiation) > 0 and len(temperature) > 0:
    #     Tmax_last = temperature[35]['t_max']
    #     Tmin_last = temperature[35]['t_min']
    #     Tmean_last = (Tmax_last + Tmin_last) / 2
    #     ea_last = 0.6108 * math.exp((17.27 * Tmean_last) / (Tmean_last + 237.2))
    #     Delta_last = 4098 * ea_last / ((Tmean_last + 237.3) ** 2)
    #     Rs_val_last = solar_radiation[35]
    #     ET0_last = (C * Rs_val_last / Lambda) * (Delta_last / (Delta_last + Gama))
    #     ET0sum += ET0_last * 5

    return ET0sum
