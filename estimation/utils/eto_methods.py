import csv
import math
from rest_framework import serializers


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
        1: ['latitude', 'elevation', 'eto_rs_data'],
        2: ['latitude', 'elevation', 'eto_sh_data'],
        3: ['latitude', 'elevation', 'eto_sh_data'],
        4: ['latitude', 'c_value', 't_mean_value'],
        5: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        6: ["latitude", "t_mean_value"],
        7: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        8: ["solar_radiation", "rh_value", "temperature"],
        9: ['latitude', 'elevation', 'solar_radiation', 'temperature'],
        10: ["c_value", "solar_radiation", "temperature"],
        11: ["c_value", 'solar_radiation'],
        12: ["solar_radiation", "t_mean_value", "p_value"]
        #     TODO: Need to add required field.
    }

    required_fields = required_fields_map.get(eto_method, [])
    missing_fields = [field for field in required_fields if data.get(field) is None]

    if missing_fields:
        missing_fields_str = ', '.join(missing_fields)
        raise serializers.ValidationError(
            f"{missing_fields_str.capitalize()} {'and' if len(missing_fields) > 1 else ''} {'are' if len(missing_fields) > 1 else 'is'} required for eto_method {eto_method}"
        )


def fao_combined_pm_method(latitude, elevation, eto_rs_data):
    """
    Calculate Yearly ET0 using the FAO Combined P-M method with Rs option 1.1.

    Args:
    - latitude (float): Latitude in decimal form.
    - elevation (float): Elevation in meters.
    - climatic_data (list): List containing climatic input data for 36 periods.
        Each period should have the format: (P, Tmax, Tmin, RH, WS, SR).

    Returns:
    - YET0 (float): Yearly ET0 value.
    """
    # Constants
    Lambda = 2.4536

    # Initialize variables
    SumET0 = 0
    daily_eto = []
    for r in range(36):
        Tmax_r = eto_rs_data[r]['Tmax_r']
        Tmin_r = eto_rs_data[r]['Tmin_r']
        RH_r = eto_rs_data[r]['RH_r']
        WS_r = eto_rs_data[r]['WS_r']
        SR_r = eto_rs_data[r]['SR_r']

        # Calculation of mean temperature
        Tmean_r = (Tmax_r + Tmin_r) / 2

        # Calculation of Ra (Extraterrestrial Radiation)
        print(r)
        J_t = (10 * r) - 5  # r starts from 0, hence +1
        del_t = 0.409 * math.sin(math.radians(0.0172 * J_t - 1.39))
        dr_t = 1 + 0.033 * math.cos(math.radians(0.0172 * J_t))
        ws_t = math.acos(-math.tan(math.radians(latitude * 22 / (180 * 7))) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * ((ws_t * math.sin(math.radians(latitude * 22 / (180 * 7))) * math.sin(del_t)) + (
                math.cos(math.radians(latitude * 22 / (180 * 7))) * math.cos(del_t) * math.sin(ws_t)))

        # Calculation of es, ea, delta
        es_Tmax_r = 0.6108 * math.exp((17.27 * Tmax_r) / (Tmax_r + 237.3))
        es_Tmin_r = 0.6108 * math.exp((17.27 * Tmin_r) / (Tmin_r + 237.3))
        es_r = (es_Tmax_r + es_Tmin_r) / 2
        ea_r = (RH_r / 100) * es_r
        Delta_r = 4098 * ea_r / ((Tmean_r + 237.3) ** 2)

        # Calculation of Rns, Rnl, Rn
        Rs_r = SR_r
        Rns_r = 0.77 * Rs_r
        Rnl_r = (4.903 * 10 ** -9) * 0.5 * (
                ((Tmax_r + 273.16) ** 4 + (Tmin_r + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea_r)) * (
                1.136 * Rs_r / (0.75 * Ra_t)) - 0.07)
        Rn_r = Rns_r - Rnl_r
        R_r = 0.408 * Delta_r * Rn_r

        # Calculation of A (Aerodynamic term)
        A_r = 900 * WS_r * (es_r - ea_r) / (Tmean_r + 273)

        # Calculation of D (Denominator part)
        D_r = Delta_r + (0.00163 * ((101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26) / Lambda)) * (1 + 0.34 * WS_r)

        # Calculation of ET0 for the current period
        ET0_r = (R_r + A_r) / D_r

        print(f'daily eto__{r}: {ET0_r:.2f} m')

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods

    return YET0


def pm_method_sh(latitude, elevation, eto_sh_data):
    Lambda = 2.4536
    SumET0 = 0

    for r in range(0, len(eto_sh_data)):
        Tmax_r = eto_sh_data[r]['Tmax_r']
        Tmin_r = eto_sh_data[r]['Tmin_r']
        RH_r = eto_sh_data[r]['RH_r']
        WS_r = eto_sh_data[r]['WS_r']
        SH_r = eto_sh_data[r]['SH_r']

        # Calculation of Ra
        J_t = 10 * r - 5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(math.radians(latitude)) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * ((ws_t * math.sin(math.radians(latitude)) * math.sin(del_t)) + (
                math.cos(math.radians(latitude)) * math.cos(del_t) * math.sin(ws_t)))
        N_t = 7.64 * ws_t
        Rs_t = (0.25 + 0.50 * SH_r / N_t) * Ra_t

        # Calculation of es, ea, delta
        es_Tmax_r = 0.6108 * math.exp((17.27 * Tmax_r) / (Tmax_r + 237.3))
        es_Tmin_r = 0.6108 * math.exp((17.27 * Tmin_r) / (Tmin_r + 237.3))
        es_r = (es_Tmax_r + es_Tmin_r) / 2
        ea_r = (RH_r / 100) * es_r
        Delta_r = 4098 * ea_r / ((Tmax_r + Tmin_r) / 2 + 237.3) ** 2

        # Calculation of Rns, Rso, Rnl, Rn
        Rns_r = 0.77 * Rs_t
        Rnl_r = (4.903 * 10 ** -9) * 0.5 * (
                ((Tmax_r + 273.16) ** 4 + (Tmin_r + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea_r)) * (
                1.136 * Rs_t / (0.75 * Ra_t)) - 0.07)
        Rn_r = Rns_r - Rnl_r
        R_r = 0.408 * Delta_r * (Rn_r - 0)

        # Calculation of A (Aerodynamic term)
        A_r = 900 * WS_r * (es_r - ea_r) / ((Tmax_r + Tmin_r) / 2 + 273)

        # Calculation of D (Denominator part)
        P = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26
        Gama = 0.00163 * P / Lambda
        D_r = Delta_r + Gama * (1 + 0.34 * WS_r)

        # Calculation of ET0 for the current period
        ET0_r = (R_r + A_r) / D_r

        print(f'Eto___{r} {ET0_r}')

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods
    return YET0


def pm_method_no_rs_sh(latitude, elevation, eto_sh_data):
    Lambda = 2.4536
    SumET0 = 0
    Lrad = latitude * 22 / (180 * 7)
    Z = elevation
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    Gama = 0.00163 * P / Lambda

    for t in range(0, len(eto_sh_data)):
        Tmax_r = eto_sh_data[t]['Tmax_r']
        Tmin_r = eto_sh_data[t]['Tmin_r']
        RH_r = eto_sh_data[t]['RH_r']
        WS_r = eto_sh_data[t]['WS_r']
        J_t = 10 * t - 5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        Ra_t = 37.6 * dr_t * (
                (ws_t * math.sin(Lrad) * math.sin(del_t)) + (math.cos(Lrad) * math.cos(del_t) * math.sin(ws_t)))
        N_t = 7.64 * ws_t
        Rs_t = 0.16 * ((Tmax_r - Tmin_r) ** 0.5) * (Ra_t / 2.4536)

        # Calculation of es, ea, delta
        es_Tmax_r = 0.6108 * math.exp((17.27 * Tmax_r) / (Tmax_r + 237.3))
        es_Tmin_r = 0.6108 * math.exp((17.27 * Tmin_r) / (Tmin_r + 237.3))
        es_r = (es_Tmax_r + es_Tmin_r) / 2
        ea_r = (RH_r / 100) * es_r
        Delta_r = 4098 * ea_r / ((Tmax_r + Tmin_r) / 2 + 237.3) ** 2

        # Calculation of Rns, Rnl, Rn
        Rns_r = 0.77 * Rs_t
        Rnl_r = (4.903 * 10 ** -9) * 0.5 * (
                ((Tmax_r + 273.16) ** 4 + (Tmin_r + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea_r)) * (
                1.136 * Rs_t / (0.75 * Ra_t)) - 0.07)
        Rn_r = Rns_r - Rnl_r
        R_r = 0.408 * Delta_r * (Rn_r - 0)

        # Calculation of A
        A_r = 900 * WS_r * (es_r - ea_r) / ((Tmax_r + Tmin_r) / 2 + 273)

        # Calculation of D
        D_r = Delta_r + Gama * (1 + 0.34 * WS_r)

        # Calculation of ET0 for the current period
        ET0_r = (R_r + A_r) / D_r

        print(f'daily eto_{t}: {ET0_r:.2f} m')

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods

    return YET0


import math
import pandas as pd


def fao_blaney_criddle_method(latitude, c_values, t_mean_value, p_value):
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
    Lrad = round(latitude * math.pi / 180, 2)

    # Initialize variables
    sumN = 0
    ET0_values = []
    intermediate_values = []

    # Create DataFrame to store intermediate values
    df = pd.DataFrame(columns=['Period', 'J_t', 'L-rad', 'del-t', 'dr-t', 'ws-t', 'N-t', 'N-t*10', 'ETO/Day'])

    # Calculate yearly N (YN) and p values
    YN = 0
    csv_data = []
    for i, T_mean in enumerate(t_mean_value):
        J_t = 10 * (i + 1) - 5
        del_t = round(0.409 * math.sin(0.0172 * J_t - 1.39), 2)
        dr_t = round(1 + 0.033 * math.cos(0.0172 * J_t), 2)
        ws_t = round(math.acos(-math.tan(Lrad) * math.tan(del_t)), 2)
        N_t = round(7.64 * ws_t, 2)
        sumN += N_t
        YN = N_t * 10

        # Calculate p values
        p_t = p_value[i]

        # Calculate ET0 values
        c_t = c_values[i]
        ET0_t = c_t * p_t * (0.46 * T_mean + 8)
        ET0_values.append(ET0_t)

        n_360 = round(N_t * 10, 2)
        ws_t_round = round(ws_t, 2)
        daily_eto = round(c_t * p_t * (0.46 * T_mean + 8), 2)

        csv_data.append([i + 1, J_t, Lrad, del_t, dr_t, ws_t_round, N_t, n_360, daily_eto])
        df.loc[i] = [i + 1, J_t, Lrad, del_t, dr_t, ws_t_round, N_t, n_360, daily_eto]

    # Calculate yearly ET0 (YET0)
    SumET0 = sum(ET0_values)
    YET0 = SumET0
    df.to_excel('fao_blaney_criddle_output.xlsx', index=False)
    return YET0


def makkink_method(latitude, elevation, solar_radiation, temperature, p_value):
    # Constants
    Lambda = 2.4536
    Lrad = math.radians(latitude)

    # Initialize variables
    ET0_sum = 0
    delta_sum = 0
    Tmean_sum = 0

    # Calculate Gamma for each P value
    Gama_values = [0.00163 * P / Lambda for P in p_value]

    # Calculate delta and Tmean for each time step and simultaneously calculate ET0
    print('Table 3-  Makkin.xlsx')
    print('-' * 30)
    for i in range(len(solar_radiation)):
        Rs = solar_radiation[i]
        temp_data = temperature[i % len(temperature)]  # Use modulo to cycle through temperature data
        P = p_value[i % len(p_value)]  # Use modulo to cycle through p_value data
        Gama = Gama_values[i % len(Gama_values)]  # Use modulo to cycle through Gama values

        # Extract temperature values
        t_max = temp_data['t_max']
        t_min = temp_data['t_min']

        # Calculate Tmean
        Tmean = (t_max + t_min) / 2
        Tmean_sum += Tmean

        # Calculate delta
        ea = 0.6108 * math.exp((17.27 * Tmean) / (Tmean + 237.2))
        delta = 4098 * ea / (Tmean + 237.3) ** 2
        delta_sum += delta

        # Calculate ET0 for the current time step
        ET0 = ((0.61 * Rs * delta) / ((delta + Gama) * Lambda)) - 0.12

        print(f'ETO___{i}: {ET0:.2f} m')
        ET0_sum += ET0 * 10  # ET0 for each time step is multiplied by 10

    print('-' * 30)

    # Calculate yearly ET0
    YET0 = ET0_sum + ((ET0 * 5) if ET0 else 0)  # Multiply the last ET0 value by 5

    return YET0


def hargreaves_method(latitude, t_mean_value):
    """
    Calculate ET0 using Hargreaves method.

    Args:
        latitude (float): Latitude in degrees.
        t_mean_value (list): List of mean temperature values for each day.

    Returns:
        float: Yearly ET0 value.

    Raises:
        ValueError: If the length of 't_mean_value' is not 36.
    """
    if len(t_mean_value) != 36:
        raise ValueError("Temperature data should be provided for 36 days.")

    # Convert latitude to radians
    phi = math.radians(latitude)

    # Initialize sumET0
    sum_et0 = 0

    # Constants
    phi_rad = phi
    lambda_value = 2.4536
    print(f'Table 4- HG .xlsx')
    print('-' * 30)
    for t in range(36):
        # Extract temperature data for the current day
        tmean = t_mean_value[t]

        # Calculate J, del, dr, ws
        j = (10 * (t + 1)) - 5
        delta = 0.409 * math.sin(0.0172 * j - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * j)
        ws = math.acos(-math.tan(phi_rad) * math.tan(delta))

        # Calculate Ra
        ra = 37.6 * dr * (
                (ws * math.sin(phi_rad) * math.sin(delta)) + (math.cos(phi_rad) * math.cos(delta) * math.sin(ws)))

        # Calculate ET0
        et0 = (0.0023 * ra / lambda_value) * (tmean + 17.8) * math.sqrt(0.75 * (tmean - 18))

        print(f'ET0__{t}: {et0:.2f} m')

        # Add ET0 to sumET0
        sum_et0 += et0
    print('-' * 30)

    # Calculate Yearly ET0
    yet0 = sum_et0

    return yet0


def hansen_method(latitude, elevation, solar_radiation, temperature):
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

    # Constants
    lambda_value = 2.4536

    # Calculate P
    z = elevation
    p = 101.3 * math.pow(((293 - 0.0065 * z) / 293), 5.26)

    # Calculate Gama
    gama = 0.00163 * p / lambda_value
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
        et0 = (0.7 * solar_radiation[k] * delta) / ((delta + gama) * lambda_value)

        print(f'et0___{k}: {et0:.2f} m')

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0


def turc_method(solar_radiation, rh_value, temperature):
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
    print('Table 6- Turk.xlsx')
    print('-' * 30)
    for t in range(36):
        tmean = (temperature[t]["t_max"] + temperature[t]["t_min"]) / 2
        rs = solar_radiation[t]
        rh = rh_value[t]

        if rh < 50:
            aT = 1 + (50 - rh) / 70
        else:
            aT = 1

        et0 = (aT * 0.013 * (tmean / (tmean + 15))) * (23.8856 * rs + 50)
        print(f'ET0__{t}: {et0:.2f} m')
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    print('-' * 30)

    yet0 = sum_et0 + (et0 * 5)
    return yet0


def priestley_taylor_method(latitude, elevation, solar_radiation, temperature):
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
    phi = math.radians(latitude)

    # Constants
    lambda_value = 2.4536

    # Calculate gama
    z = elevation
    p = 101.3 * (((293 - 0.0065 * z) / 293) ** 5.26)
    gama = 0.00163 * p / lambda_value

    sum_et0 = 0
    print(f'Table 7- P-T.xlsx')
    print('-' * 30)
    for k in range(36):
        # Calculate Tmean
        tmax = temperature[k]["t_max"]
        tmin = temperature[k]["t_min"]
        tmean = (tmax + tmin) / 2

        # Calculate Delta
        ea = 0.6108 * math.exp((17.27 * tmean) / (tmean + 237.2))
        delta = (4098 * ea) / ((tmean + 237.3) ** 2)

        # Calculate Ra
        j = (10 * (k + 1)) - 5
        delta_rad = 0.409 * math.sin(0.0172 * j - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * j)
        ws = math.acos(-math.tan(phi) * math.tan(delta_rad))
        ra = 37.6 * dr * (
                (ws * math.sin(phi) * math.sin(delta_rad)) + (math.cos(phi) * math.cos(delta_rad) * math.sin(ws))
        )

        # Calculate Rn
        rs = solar_radiation[k]
        rns = 0.77 * rs
        rnl = (4.903 * (10 ** -9)) * 0.5 * (
                ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea)) * (
                1.136 * rs / (0.75 * ra)) - 0.07)
        rn = rns - rnl

        # Calculate ET0
        et0 = 1.26 * (delta / (delta + gama)) * ((rn - 0) / lambda_value)
        print(f'ET0__{k}: {et0:.2f} m')
        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    print('-' * 30)

    yet0 = sum_et0 + (et0 * 5)
    return yet0


def jensen_haise_method(c_value, solar_radiation, temperature):
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

    sum_et0 = 0
    print('Table 8  -Jensen-Haise.xlsx')
    print('-' * 30)
    for k in range(36):
        # Calculate Tmean
        tmean = (temperature[k]["t_max"] + temperature[k]["t_min"]) / 2

        # Calculate ET0
        et0 = c_value[k] * (solar_radiation[k] * (0.025 * tmean + 0.08) / lambda_value)
        print(f'ET0__{k}: {et0:.2f} m')
        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)
    print('-' * 30)
    return yet0


def abtew_method(c_value, solar_radiation):
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
    print('Table 9- Abtew .xlsx')
    print('-' * 30)
    for j in range(36):
        # Calculate ET0
        et0 = c_value[j] * (ki * solar_radiation[j] / lambda_value)
        print(f'ET0__{j}: {et0:.2f} m')
        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)
    print('-' * 30)

    return yet0


def de_bruin_method(solar_radiation, t_mean_value, p_value):
    # Constants
    C = 0.65
    Lambda = 2.4536
    gamma_values = [0.00163 * P / Lambda for P in p_value]
    # Variables for calculation
    Delta_values = []
    ET0_sum = 0
    # Calculate Delta for each Tmean value
    for T in t_mean_value:
        ea = 0.6108 * math.exp((17.27 * T) / (T + 237.2))
        Delta = 4098 * ea / ((T + 237.2) ** 2)
        Delta_values.append(Delta)
    for Rs_val, T_val, Delta_val, gamma_val in zip(solar_radiation, t_mean_value, Delta_values, gamma_values):
        ET0 = (C * Rs_val / Lambda) * (Delta_val / (Delta_val + gamma_val))
        ET0_sum += ET0
    # Multiply by 10 to get daily value
    ET0_sum *= 10
    # Add the last value of ET0 for 5 days
    ET0_sum += ET0 * 5
    return ET0_sum

#
# # Example usage with provided data
# Rs_data = [12.1, 12.1, 12.1, 12.2, 12.2, 12.2, 17.6, 17.6, 17.6, 18.4, 18.4, 18.4,
#            15.5, 15.5, 15.5, 13.7, 13.7, 13.7, 14.1, 14.1, 14.1, 12.3, 12.3, 12.3,
#            12.9, 12.9, 12.9, 14.3, 14.3, 14.3, 12.2, 12.2, 12.2, 8.8, 8.8, 8.8]
#
# Tmean_data = [18.95, 18.95, 18.95, 19.85, 19.85, 19.85, 24.45, 24.45, 24.45, 27.8,
#               27.8, 27.8, 28.75, 28.75, 28.75, 29.4, 29.4, 29.4, 29.6, 29.6, 29.6,
#               29, 29, 29, 28.9, 28.9, 28.9, 27.5, 27.5, 27.5, 24, 24, 24, 18.75,
#               18.75, 18.75]
#
# latitude = 37.7749  # Example latitude in degrees (San Francisco)
# elevation = 150  # Example elevation in meters
#
# # Example P values from the data
# P_values = [12.1, 12.1, 12.1, 18.7, 18.7, 18.7, 159.0, 159.0, 159.0, 260.0, 260.0, 260.0,
#             53.7, 53.7, 53.7, 115.3, 115.3, 115.3, 100.0, 100.0, 100.0, 189.7, 189.7, 189.7,
#             131.7, 131.7, 131.7, 51.0, 51.0, 51.0, 0, 0, 0, 0, 0, 0]
#
# ET0_result = calculate_ET0(Rs_data, Tmean_data, latitude, elevation, P_values)
