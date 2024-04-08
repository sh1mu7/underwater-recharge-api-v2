import math

from rest_framework import serializers


def fao_combined_pm_method(latitude, elevation, climatic_data):
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

    print(f'climatic_data: {climatic_data}\n climatic_data_type: {type(climatic_data)}')

    for r in range(36):
        P_r = climatic_data[r]['P_r']
        Tmax_r = climatic_data[r]['Tmax_r']
        Tmin_r = climatic_data[r]['Tmin_r']
        RH_r = climatic_data[r]['RH_r']
        WS_r = climatic_data[r]['WS_r']
        SR_r = climatic_data[r]['SR_r']

        # Calculation of mean temperature
        Tmean_r = (Tmax_r + Tmin_r) / 2

        # Calculation of Ra (Extraterrestrial Radiation)
        J_t = (10 * (r + 1)) - 5  # r starts from 0, hence +1
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

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods

    return YET0


def pm_method_sh(latitude, elevation, climatic_data):
    Lambda = 2.4536
    SumET0 = 0
    print(f'length of climatic_data: {len(climatic_data)}')

    for r in range(1, len(climatic_data)):
        P_r = climatic_data[r]['P_r']
        Tmax_r = climatic_data[r]['Tmax_r']
        Tmin_r = climatic_data[r]['Tmin_r']
        RH_r = climatic_data[r]['RH_r']
        WS_r = climatic_data[r]['WS_r']
        SH_r = climatic_data[r]['SH_r']

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

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods

    return YET0


def pm_method_no_rs_sh(latitude, elevation, climatic_data):

    Lambda = 2.4536
    SumET0 = 0
    Lrad = latitude * 22 / (180 * 7)
    Z = elevation
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    Gama = 0.00163 * P / Lambda

    for t in range(1, len(climatic_data)):
        P_r = climatic_data[t]['P_r']
        Tmax_r = climatic_data[t]['Tmax_r']
        Tmin_r = climatic_data[t]['Tmin_r']
        RH_r = climatic_data[t]['RH_r']
        WS_r = climatic_data[t]['WS_r']
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

        print(f"Delta_r: {Delta_r}, type: {type(Delta_r)}")

        # Calculation of Rns, Rnl, Rn
        Rns_r = 0.77 * Rs_t
        Rnl_r = (4.903 * 10 ** -9) * 0.5 * (
                ((Tmax_r + 273.16) ** 4 + (Tmin_r + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea_r)) * (
                1.136 * Rs_t / (0.75 * Ra_t)) - 0.07)
        Rn_r = Rns_r - Rnl_r
        R_r = 0.408 * Delta_r * (Rn_r - 0)

        print(f"R_r: {R_r}, type: {type(R_r)}")

        # Calculation of A
        A_r = 900 * WS_r * (es_r - ea_r) / ((Tmax_r + Tmin_r) / 2 + 273)

        print(f"A_r: {A_r}, type: {type(A_r)}")

        # Calculation of D
        D_r = Delta_r + Gama * (1 + 0.34 * WS_r)

        print(f"D_r: {D_r}, type: {type(D_r)}")

        # Calculation of ET0 for the current period
        ET0_r = (R_r + A_r) / D_r

        print(f"ET0_r: {ET0_r}, type: {type(ET0_r)}")

        # Accumulate ET0 for SumET0
        SumET0 += ET0_r * 10  # Considering 10-day periods

    # Calculation of Yearly ET0
    YET0 = SumET0 + (ET0_r * 5)  # Multiply by 5 as there are 36 periods

    print(f"\nYearly ET0: {YET0}")
    return YET0


def fao_blaney_criddle_method(latitude, c_values, temperature_data):
    # Convert latitude to radians
    Lrad = latitude * 22 / (180 * 7)

    # Initialize variables
    sumN = 0
    ET0_values = []

    # Calculate yearly N (YN) and p values
    YN = 0
    p_values = []
    for i, temp_data in enumerate(temperature_data):
        J_t = 10 * (i + 1) - 5
        del_t = 0.409 * math.sin(0.0172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(del_t))
        N_t = 7.64 * ws_t
        sumN += N_t
        YN += N_t * 10

        # Calculate p values
        p_t = 100 * (N_t / YN)
        p_values.append(p_t)

        # Calculate mean temperature
        T_mean = (temp_data['t_max'] + temp_data['t_min']) / 2

        # Calculate ET0 values
        c_t = c_values[i]
        ET0_t = c_t * p_t * (0.46 * T_mean + 8)
        ET0_values.append(ET0_t)

    # Calculate yearly ET0 (YET0)
    SumET0 = sum(ET0_values)
    YET0 = SumET0 + ET0_values[-1] * 5

    return YET0


def makkink_method(latitude, elevation, rs_data, temperature_data):
    # Constants
    Lambda = 2.4536
    Lrad = math.radians(latitude)

    # Calculate atmospheric pressure
    Z = elevation
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26

    # Calculate Gamma
    Gama = 0.00163 * P / Lambda

    # Initialize variables
    ET0_sum = 0
    delta_sum = 0
    Tmean_sum = 0

    # Calculate delta and Tmean for each time step and simultaneously calculate ET0
    for i in range(len(rs_data)):
        Rs = rs_data[i]
        temp_data = temperature_data[i % len(temperature_data)]  # Use modulo to cycle through temperature data

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
        ET0_sum += ET0 * 10  # ET0 for each time step is multiplied by 10

    # Calculate yearly ET0
    YET0 = ET0_sum + ((ET0 * 5) if ET0 else 0)  # Multiply the last ET0 value by 5

    return YET0


def hargreaves_method(latitude, temperature_data):
    """
    Calculate ET0 using Hargreaves method.

    Args:
    - latitude (float): Latitude in degrees.
    - temperature_data (list): List of dictionaries containing temperature data for each day.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    if len(temperature_data) != 36:
        raise ValueError("Temperature data should be provided for 36 days.")

    # Convert latitude to radians
    phi = math.radians(latitude)

    # Initialize sumET0
    sum_et0 = 0

    # Constants
    phi_rad = phi
    lambda_value = 2.4536

    for t in range(36):
        # Extract temperature data for the current day
        tmax = temperature_data[t]["t_max"]
        tmin = temperature_data[t]["t_min"]

        # Calculate J, del, dr, ws
        j = (10 * (t + 1)) - 5
        delta = 0.409 * math.sin(0.0172 * j - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * j)
        ws = math.acos(-math.tan(phi_rad) * math.tan(delta))

        # Calculate Ra
        ra = 37.6 * dr * (
                (ws * math.sin(phi_rad) * math.sin(delta)) + (math.cos(phi_rad) * math.cos(delta) * math.sin(ws)))

        # Calculate ET0
        tmean = (tmax + tmin) / 2
        et0 = (0.0023 * ra / lambda_value) * (tmean + 17.8) * math.sqrt(tmax - tmin)

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0


def hansen_method(latitude, elevation, rs_value, temperature_data):
    """
    Calculate ET0 using Hansen (1984) method.

    Args:
    - temperature_data (list): List of dictionaries containing maximum and minimum temperature data for 36 days.
    - rs_value (list): List of Rs values for 36 days.
    - latitude (float): Latitude in degrees.
    - elevation (float): Elevation in meters.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    if len(temperature_data) != 36 or len(rs_value) != 36:
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

    for k in range(36):
        # Calculate Tmean
        t_max = temperature_data[k]['t_max']
        t_min = temperature_data[k]['t_min']
        t_mean = (t_max + t_min) / 2

        # Calculate delta
        ea = 0.6108 * math.exp((17.27 * t_mean) / (t_mean + 237.2))
        delta = 4098 * ea / math.pow((t_mean + 237.3), 2)

        # Calculate ET0
        et0 = (0.7 * rs_value[k] * delta) / ((delta + gama) * lambda_value)

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0


def turc_method(rs_value, rh_value, temperature_data):
    """
    Calculate ET0 using Turc method.

    Args:
    - temperature_data (list): List of dictionaries containing Tmax and Tmin for 36 days.
    - rs_data (list): List of Rs values for 36 days.
    - rh_data (list): List of RH values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """

    print(f'Temperature: {temperature_data}')
    if len(temperature_data) != 36 or len(rs_value) != 36 or len(rh_value) != 36:
        raise ValueError("Data should be provided for all 36 days.")

    # Initialize sumET0
    sum_et0 = 0

    for t in range(36):
        tmean = (temperature_data[t]["t_max"] + temperature_data[t]["t_min"]) / 2
        rs = rs_value[t]
        rh = rh_value[t]

        if rh < 50:
            aT = 1 + (50 - rh) / 70
        else:
            aT = 1

        et0 = (aT * 0.013 * (tmean / (tmean + 15))) * (23.8856 * rs + 50)
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)
    return yet0


def priestley_taylor_method(latitude, elevation, rs_value, temperature_data):
    """
    Calculate ET0 using the Priestley-Taylor method.

    Args:
    - latitude (float): Latitude in degrees.
    - elevation (float): Elevation in meters.
    - temperature_data (list): List of dictionaries containing Tmax and Tmin for 36 days.
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

    for k in range(36):
        # Calculate Tmean
        tmax = temperature_data[k]["t_max"]
        tmin = temperature_data[k]["t_min"]
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
        rs = rs_value[k]
        rns = 0.77 * rs
        rnl = (4.903 * (10 ** -9)) * 0.5 * (
                ((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) * (0.34 - 0.139 * math.sqrt(ea)) * (
                1.136 * rs / (0.75 * ra)) - 0.07)
        rn = rns - rnl

        # Calculate ET0
        et0 = 1.26 * (delta / (delta + gama)) * ((rn - 0) / lambda_value)

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)
    return yet0


def jensen_haise_method(c_value, rs_value, temperature_data):
    """
    Calculate ET0 using Jensen-Haise method.

    Args:
    - temperature_data (list): List of dictionaries containing Tmean for 36 days.
    - rs_values (list): List of Rs values for 36 days.
    - c_values (list): List of C values for 36 days.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    if len(temperature_data) != 36 or len(rs_value) != 36 or len(c_value) != 36:
        raise ValueError("Temperature, Rs, and C data should be provided for all 36 days.")

    # Constants
    lambda_value = 2.4536

    sum_et0 = 0

    for k in range(36):
        # Calculate Tmean
        tmean = (temperature_data[k]["t_max"] + temperature_data[k]["t_min"]) / 2

        # Calculate ET0
        et0 = c_value[k] * (rs_value[k] * (0.025 * tmean + 0.08) / lambda_value)

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0


def abtew_method(c_value, rs_value):
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

    for j in range(36):
        # Calculate ET0
        et0 = c_value[j] * (ki * rs_value[j] / lambda_value)

        # Add ET0 to sumET0
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0


def de_bruin_method(rs_value, temperature_data, p):
    """
    Calculate potential evapotranspiration (PET) using de Bruin method.

    Args:
    - rs_values (list): List of Rs values for 36 days.
    - temperature_data (list): List of dictionaries containing Tmean for 36 days.
    - L (float): Latitude in degrees.
    - El (float): Elevation in meters.

    Returns:
    - yet0 (float): Yearly ET0 value.
    """
    # Constants
    c_value = 0.65
    lambda_value = 2.4536

    # Calculate p and update gama
    # Lrad = latitude * (22 / (180 * 7))
    # p = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26
    gama = 0.00163 * p / lambda_value

    # Calculate ET0
    sum_et0 = 0
    for q in range(36):
        tmax = temperature_data[q]["t_max"]
        tmin = temperature_data[q]["t_min"]
        tmean = (tmax + tmin) / 2
        ea = 0.6108 * math.exp((17.27 * tmean) / (tmean + 237.2))
        delta = 4098 * ea / ((tmean + 237.3) ** 2)
        et0 = (c_value * rs_value[q] / lambda_value) * (delta / (delta + gama))
        sum_et0 += et0 * 10

    # Calculate Yearly ET0
    yet0 = sum_et0 + (et0 * 5)

    return yet0
