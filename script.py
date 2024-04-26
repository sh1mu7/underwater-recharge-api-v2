import math
import random
from cmath import exp
import matplotlib.pyplot as plt


def select_recharge_estimation_method():
    """
    Prompt user to select the method of recharge estimation (WB method or WTF method).
    """
    print("Select Method of Recharge Estimation:")
    print("a. WB method")
    print("b. WTF method")
    method = input("Enter your choice (a or b): ")
    if method == 'a':
        wb_method()
    elif method == 'b':
        wtf_method()
    else:

        print("Invalid choice. Please select a valid option.")


def wb_method():
    """
    Perform data acquisition for WB method.
    """
    catchment_area = float(input("Enter Catchment area (in Km2): "))
    print("Enter Recharge Limiting Conditions:")
    print("1. Potential recharge is higher than the storage capacity of the aquifer (recharge opportunity)")
    print("2. Potential recharge (Rp) is less than the recharge opportunity (Rop)")
    print("3. Potential recharge (Rp) is equal to the recharge opportunity (Rop)")
    rlc = int(input("Enter your choice (1, 2, or 3): "))
    if rlc == 1:
        rp = float(
            input("Enter reduction factor (Rp) to actual recharge (Ra) (1-0.2, 0.8 means 20% reduction, etc.): "))
    print("Select Generous Classification of the Area:")
    print("1. Arid (P ≤ 500 mm)")
    print("2. Semi-arid (500 < P < 1000)")
    print("3. Semi-humid (1000 < P < 1500)")
    print("4. Humid (P > 1500)")
    classification = int(input("Enter your choice (1, 2, 3, or 4): "))
    print("Select ETo Calculation Method:")
    print("i. P-M method")
    print("ii. FAO Blaney-Cridle method")
    print("iii. Hargreaves method")
    print("iv. Makkink method")
    print("v. Hansen method")
    print("vi. Modified Makkink method")
    print("vii. Prestley-Taylor method")
    et0_option = input("Enter your choice (i, ii, iii, iv, v, vi, or vii): ")
    if et0_option == 'i':
        YET0 = pm_method()
        print(f"Yearly ET0 (P-M method) = {YET0}")
    elif et0_option == 'ii':
        YET0 = hargreaves_method()  # Placeholder for Hargreaves method
        print(f"Hargreaves method value = {YET0}")
    elif et0_option == 'iii':
        YET0 = blaney_criddle_method()  # Placeholder for Hargreaves method
        print(f" BlenyCridle method value = {YET0}")
    elif et0_option == 'iv':
        YET0 = makkink_method()
        print(f" Makkink method value = {YET0}")  # Placeholder for Makkink method
    elif et0_option == 'v':
        hansen_method()  # Placeholder for Hansen method
    elif et0_option == 'vi':
        modified_makkink_method()  # Placeholder for Modified Makkink method
    elif et0_option == 'vii':
        prestley_taylor_method()  # Placeholder for Prestley-Taylor method
    else:
        print("Selected ETo Calculation Method is not supported.")
    # Perform further calculations based on the selected method


def pm_method():
    """
    Perform ET0 calculation using the P-M method.
    """
    # Ask for Latitude and Elevation
    L = float(input("Enter Latitude (in decimal degrees): "))
    EL = float(input("Enter Elevation (in meters): "))

    # Read climatic input data
    print("Enter Climatic input data (10 days):")
    for r in range(1, 37):
        Pr = float(input("Precipitation (mm): "))
        Tmaxr = float(input("Maximum temperature (°C): "))
        Tminr = float(input("Minimum temperature (°C): "))
        RHr = float(input("Relative Humidity (%): "))
        SRr = float(input("Solar Radiation (MJ/m2/d): "))
        WSr = float(input("Wind Speed (m/s): "))
        # Data checking
        if Tmaxr > 50:
            print(f"Max. Temp. is > 50: {Tmaxr}. Check the data. Stopping.")
            return
        if Tminr < -10:
            print(f"Min. Temp. is < -10: {Tminr}. Check the data. Stopping.")
            return
        if RHr > 99:
            print(f"RH > 99: {RHr}. Check the data. Stopping.")
            return
        if RHr < 25:
            print(f"RH < 25: {RHr}. Check the data. Stopping.")
            return
        if SRr > 30:
            print(f"Solar Radiation > 30: {SRr}. Check the data. Stopping.")
            return
        if SRr < 0:
            print(f"Solar Radiation < 0: {SRr}. Check the data. Stopping.")
            return
        if WSr > 5:
            print(f"Av. Wind speed > 5: {WSr}. Check the data. Stopping.")
            return
        if WSr < 0:
            print(f"Wind speed < 0: {WSr}. Check the data. Stopping.")
            return

    # Calculation of Radiation term (R)
    R = []
    G = 0
    for k in range(1, 37):
        Tk = (Tmaxr + Tminr) / 2
        ea_k = 0.611 * exp((17.2 * Tk) / (Tk + 273.2))
        Del_k = 4098 * ea_k / (Tk + 273.2) ** 2
        R_k = 0.408 * Del_k * (SRr - G)
        R.append(R_k)

    # Calculation of Aerodynamic term (A)
    A = []
    Lemda = 2.45
    Z = EL
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    Gama = 0.00163 * P / Lemda
    for m in range(1, 37):
        ea_Tmax_m = 0.611 * exp((17.27 * Tmaxr) / (Tmaxr + 273.3))
        ea_Tmin_m = 0.611 * exp((17.27 * Tminr) / (Tminr + 273.3))
        ed_m = RHr / ((50 / ea_Tmin_m) + (50 / ea_Tmax_m))
        A_m = 900 * WSr * (ea_Tmax_m - ed_m) / (Tk + 273)
        A.append(A_m)

    # Calculation of Denominator part (D)
    D = []
    for q in range(1, 37):
        D_q = Del_k + Gama * (1 + 0.34 * WSr)
        D.append(D_q)

    # Calculation of ET0
    SumET0 = 0
    for r in range(1, 37):
        ET0_r = (R[r] + A[r]) / D[r]
        SumET0 += ET0_r * 10  # Summing up for 360 days

    YET0 = SumET0 + ET0_r * 5  # Yearly ET0 for 365 days
    return YET0


def hargreaves_method():
    """
    Perform ET0 calculation using the Hargreaves method.
    """
    # Read latitude
    L = float(input("Enter Latitude (in degrees): "))
    Lrad = L * (22 / (180 * 7))
    # Placeholder for calculating average temperature
    Tmean = []

    # Calculate Tmean for each time period
    # for i in range(1, 37):
    #     Tmax = float(input(f"Enter Max Temperature for period {i}: "))
    #     Tmin = float(input(f"Enter Min Temperature for period {i}: "))
    #     Tmean.append((Tmax + Tmin) / 2)

    for i in range(1, 37):
        Tmax = random.uniform(15, 20)
        Tmin = random.uniform(5, 10)
        Tmean.append((Tmax + Tmin) / 2)

        # TODO: Need to adjust

    # Placeholder for storing ET0 values for each time period
    ET0 = []

    # Calculate Ra and ET0 for each time period
    for t in range(1, 37):
        J = 10 * t - 5
        delta = 0.409 * math.sin(0.172 * J - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * J)
        ws = math.cos(-math.tan(Lrad) * math.tan(delta))
        Ra = 37.6 * dr * ((ws * math.sin(Lrad) * math.sin(delta)) + (math.cos(Lrad) * math.cos(delta) * math.sin(ws)))
        ET0_t = (0.0023 * Ra) * (Tmean[t - 1] + 17.8) * (Tmean[t - 1]) ** 0.5
        ET0.append(ET0_t)

    # Sum up ET0
    SumET0 = sum(ET0)

    # Calculate yearly ET0
    YET0 = SumET0 + ET0[-1] * 5

    return YET0


def blaney_criddle_method():
    """
    Perform ET0 calculation using the Blaney-Criddle method.
    """
    # Read latitude
    L = float(input("Enter Latitude (in degrees): "))
    Lrad = L * (22 / (180 * 7))

    # Placeholder for reading c and Tmean value from Table
    # For simplicity, let's assume we have predefined values in a dictionary
    temperature_data = {
        1: (20, 1.2),
        2: (21, 1.3),
        # Add more data as needed
    }

    # Calculate N, sum up, then p
    sumN = 0
    N = []
    for t in range(1, 37):
        J = 10 * t - 5
        delta = 0.409 * math.sin(0.172 * J - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * J)
        ws = math.acos(-math.tan(Lrad) * math.tan(delta))
        N_t = 7.64 * ws
        sumN += N_t
        N.append(N_t)

    # Sum up yearly N (YN)
    YN = sumN + (N[-1] * 5)

    # Calculation of p
    p = []
    for t in range(1, 37):
        p_t = 100 * (N[t - 1] * 10 / YN)
        p.append(p_t)

    # ET0 calculation
    SumET0 = 0
    for t in range(1, 37):
        Tmean = temperature_data[t][0]  # Assuming temperature data is available for each time period
        C = temperature_data[t][1]  # Assuming c value is available for each time period
        ET0_t = C * p[t - 1] * (0.46 * Tmean + 8)
        SumET0 += ET0_t * 10

    # Yearly ET0 calculation (YET0)
    YET0 = SumET0 + (ET0_t * 5)

    return YET0


def makkink_method():
    """
    Perform ET0 calculation using the Makkink method.
    """
    # Read latitude and elevation
    L = float(input("Enter Latitude (in degrees): "))
    El = float(input("Enter Elevation (in meters): "))

    # Convert latitude to radians
    Lrad = L * (22 / (180 * 7))

    # Calculate gamma
    Lambda = 2.45
    Z = El
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    Gama = 0.00163 * P / Lambda

    # Placeholder for storing Rs values
    Rs_values = []

    # Placeholder for storing temperature data
    temperature_data = []

    # Read temperature data for each time period
    for i in range(1, 37):
        Tmax = random.uniform(15, 25)
        Tmin = random.uniform(5, 10)
        temperature_data.append((Tmax, Tmin))
        # TODO: Need to adjust

    # Calculate Rs for each time period
    for Tmax, Tmin in temperature_data:
        J = (10 * 15) - 5  # Example value
        delta = 0.409 * math.sin(0.172 * J - 1.39)
        dr = 1 + 0.033 * math.cos(0.0172 * J)
        ws = math.acos(max(min(-math.tan(Lrad) * math.tan(delta), 1), -1))
        Ra = 37.6 * dr * ((ws * math.sin(Lrad) * math.sin(delta)) + (math.cos(Lrad) * math.cos(delta) * math.sin(ws)))
        Rs = 0.16 * Ra * math.sqrt(Tmax - Tmin)
        Rs_values.append(Rs)

    # Placeholder for storing ET0 values for each time period
    ET0_values = []

    # Calculate ET0 for each time period
    for Rs in Rs_values:
        delta = 4098 * math.exp((17.2 * ((Tmax + Tmin) / 2)) / (((Tmax + Tmin) / 2) + 273.2)) / (
                ((Tmax + Tmin) / 2) + 273.2) ** 2
        ET0 = (0.61 * Rs * delta) / ((delta + Gama) * 2.45) - 0.12
        ET0_values.append(ET0)

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 37), Rs_values, label='Rs')
    plt.plot(range(1, 37), ET0_values, label='ET0')
    plt.xlabel('Time Period')
    plt.ylabel('Values')
    plt.title('Variation of Rs and ET0 over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Calculate SumET0
    SumET0 = sum(ET0_values)

    # Calculate yearly ET0 (YET0) for 365 days
    YET0 = SumET0 + ET0_values[-1] * 5

    return YET0


def hansen_method():
    """
    Perform ET0 calculation using the Hansen method.
    """
    # Read latitude and elevation
    L = float(input("Enter Latitude (in degrees): "))
    El = float(input("Enter Elevation (in meters): "))
    Lrad = L * (22 / (180 * 7))

    # Calculate Gamma
    Lambda = 2.45
    Z = El
    P = 101.3 * ((293 - 0.0065 * Z) / 293) ** 5.26
    Gama = 0.00163 * P / Lambda

    # Read max and min temperatures
    Tmean = []
    for k in range(1, 37):
        Tmax_k = random.uniform(20, 25)
        Tmin_k = random.uniform(-5, 5)
        Tmean.append((Tmax_k + Tmin_k) / 2)

        # TODO: Need to adjust

    # Calculate Ra and Rs
    Ra_values = []
    Rs_values = []
    for t in range(1, 37):
        J_t = 10 * t - 5
        delta_t = 0.409 * math.sin(0.172 * J_t - 1.39)
        dr_t = 1 + 0.033 * math.cos(0.0172 * J_t)
        ws_t = math.acos(-math.tan(Lrad) * math.tan(delta_t))
        Ra_t = 37.6 * dr_t * (
                (ws_t * math.sin(Lrad) * math.sin(delta_t)) + (math.cos(Lrad) * math.cos(delta_t) * math.sin(ws_t)))
        Rs_t = 0.16 * Ra_t * (Tmean[t - 1] - Tmin_k) ** 0.5
        Ra_values.append(Ra_t)
        Rs_values.append(Rs_t)

    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 37), Ra_values, label='Ra')
    plt.plot(range(1, 37), Rs_values, label='Rs')
    plt.xlabel('Time Period')
    plt.ylabel('Radiation (MJ/m2/day)')
    plt.title('Variation of Ra and Rs over Time')
    plt.legend()
    plt.grid(True)
    plt.show()
    # Calculate delta
    delta_values = [4098 * (0.611 * math.exp((17.2 * T) / (T + 273.2))) / ((T + 273.2) ** 2) for T in Tmean]

    # Calculate ET0 for each time period
    ET0_sum = 0
    for q in range(1, 37):
        ET0_q = (0.7 * delta_values[q - 1] * Rs_values[q - 1]) / ((delta_values[q - 1] + Gama) * Lambda)
        ET0_sum += ET0_q * 10

    # Calculate yearly ET0
    YET0 = ET0_sum + ET0_q * 5

    return YET0


def modified_makkink_method():
    print('Not implemented yet')
    pass


def prestley_taylor_method():
    print('Not implemented yet')
    pass


def wtf_method():
    """
    Perform data acquisition and calculation for WTF method.
    """
    # Read basic data
    A = float(input("Enter Catchment area (in Km2): "))
    WTmax = float(input("Enter maximum water table (WTmax): "))
    WTmin = float(input("Enter minimum water table (WTmin): "))
    NL = int(input("Enter number of layers (NL): "))

    # Read input Q data
    print("Reading input Q data...")
    Sum_Q = 0
    input_values = []
    for n in range(1, 13):
        QP_n = random.uniform(10, 10)
        QB_n = random.uniform(8, 8)
        Qin_n = random.uniform(5, 5)
        Qout_n = random.uniform(3, 3)
        Qr_n = random.uniform(1, 1)
        input_values.append([QP_n, QB_n, Qin_n, Qout_n, Qr_n])

    # Calculate total sum of input values
    Sum_Q = sum(sum(month_data) for month_data in input_values)

    # Calculate D (depth) and Sp. yield
    D = (Sum_Q / A) * 0.001

    # Read input Table-2 for Sp. yield
    print("Reading Sp. yield data...")
    Sp_yield_data = []
    for s in range(1, NL):
        LH_s = float(input(f"Enter Layer height (LH) for layer {s}: "))
        Y_s = float(input(f"Enter Sp. yield (Y) for layer {s} in percentage: "))
        Sp_yield_data.append((LH_s, Y_s))

    # Calculate Composite Sy (Yc)
    SumY = sum(LH * Y for LH, Y in Sp_yield_data)
    Yc = SumY / sum(LH for LH, _ in Sp_yield_data)

    # Calculate WTD and Re
    WTD = WTmax - WTmin
    Re = WTD / Yc

    # Time for Recharge calculation; Taking Year
    T = float(input("Enter the time for Recharge calculation (year): "))
    Re /= T
    # Calculating Runoff (RO)
    RO = Sum_Q - Re * A
    # Checking whether Precipitation is given
    Precipitation_response = int(input("Is Precipitation given? (1 for yes, 0 for no): "))
    if Precipitation_response == 0:
        print("Skipping Precipitation comparison...")
    else:
        Precipitation_percentage = float(input("Enter Precipitation percentage: "))
        Ratio = 100 * Re / Precipitation_percentage
        if Ratio > 40:
            print(f"The Calculated Recharge (mm) is: {Re}. Seems high!! Please Check the input Data.")
            return

    print(f"Yearly Recharge (mm) = {Re}")

    plt.figure(figsize=(10, 6))
    plt.bar(['Runoff', 'Recharge'], [RO, Re], color=['red', 'blue'])
    plt.xlabel('Parameters')
    plt.ylabel('Values (mm)')
    plt.title('Comparison of Runoff and Recharge')
    plt.show()


if __name__ == '__main__':
    select_recharge_estimation_method()

# Data format for wtf_method()
wtf_method = {
    "catchment_area": 100,
    "wt_max": 50,
    "wt_min": 20,
    "num_layers": 3,
    "sp_yield_data": [
        {
            "layer_height": 10,
            "sp_yield_percentage": 20
        },
        {
            "layer_height": 15,
            "sp_yield_percentage": 30
        },
        {
            "layer_height": 20,
            "sp_yield_percentage": 25
        }
    ],
    "time_period": 5,
    "is_perception_given": True,
    "precipitation_percentage": 50,
    "Q_data": [
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1},
        {"QP_n": 10, "QB_n": 8, "Qin_n": 5, "Qout_n": 3, "Qr_n": 1}
    ]
}

# blaney_criddle_method = {
#     "catchment_area": 10,
#     "rlc": 1,
#     "rp": 0,
#     "classification": 1,
#     "eto_method": 2,
#     "temperature": [
#         {"t_max": 30.5, "t_min": 21.2},
#         {"t_max": 28.9, "t_min": 22.6},
#         {"t_max": 33.7, "t_min": 19.8},
#         {"t_max": 25.3, "t_min": 18.4},
#         {"t_max": 29.8, "t_min": 20.9},
#         {"t_max": 32.1, "t_min": 21.7},
#         {"t_max": 31.6, "t_min": 23.4},
#         {"t_max": 27.4, "t_min": 22.0},
#         {"t_max": 30.9, "t_min": 21.5},
#         {"t_max": 26.7, "t_min": 19.2},
#         {"t_max": 33.2, "t_min": 20.3},
#         {"t_max": 29.5, "t_min": 22.8},
#         {"t_max": 27.8, "t_min": 21.3},
#         {"t_max": 31.8, "t_min": 20.7},
#         {"t_max": 30.2, "t_min": 21.9},
#         {"t_max": 28.6, "t_min": 22.4},
#         {"t_max": 32.4, "t_min": 19.7},
#         {"t_max": 29.3, "t_min": 21.1},
#         {"t_max": 25.9, "t_min": 20.5},
#         {"t_max": 31.0, "t_min": 20.2},
#         {"t_max": 27.5, "t_min": 19.8},
#         {"t_max": 30.3, "t_min": 20.8},
#         {"t_max": 29.7, "t_min": 22.3},
#         {"t_max": 32.0, "t_min": 21.0},
#         {"t_max": 28.2, "t_min": 19.9},
#         {"t_max": 30.8, "t_min": 22.1},
#         {"t_max": 26.8, "t_min": 20.6},
#         {"t_max": 31.2, "t_min": 21.6},
#         {"t_max": 28.7, "t_min": 20.4},
#         {"t_max": 29.0, "t_min": 22.7},
#         {"t_max": 33.5, "t_min": 20.0},
#         {"t_max": 27.9, "t_min": 21.8},
#         {"t_max": 31.5, "t_min": 19.5},
#         {"t_max": 29.4, "t_min": 21.4},
#         {"t_max": 26.4, "t_min": 20.1},
#         {"t_max": 30.6, "t_min": 22.2}
#     ],
#     "latitude": 40.5
# }


def handle_land_use_area(land_use_area):
    for L, row in enumerate(land_use_area, 1):
        SM_L = sum(row.values())
        ER_L = 100 - SM_L
        if -5 <= ER_L <= 0:
            land_use_area[L - 1]["a7"] -= ER_L
        elif 0 < ER_L <= 5:
            land_use_area[L - 1]["a7"] += ER_L
        else:
            return Response(
                {"error": f"Sum of land-use components must be equal to 100, Line number {L}, Stop"},
                status=status.HTTP_400_BAD_REQUEST
            )

def calculate_eto_method(eto_method, latitude, elevation, climatic_data_pm_full, climatic_data_pm_sh, temperature_data):
    YETO = None
    try:
        if eto_method == constants.ETO_METHOD_CHOICES.FAO_COMBINED_PM_METHOD:
            climate_data_instances = [ClimateDataPMFull.objects.create(**data) for data in climatic_data_pm_full]
            YETO = eto_methods.fao_combined_pm_method(latitude, elevation, climatic_data_pm_full)
        elif eto_method == constants.ETO_METHOD_CHOICES.PM_SH:
            climate_data_instances = [ClimateDataPMSH.objects.create(**data) for data in climatic_data_pm_sh]
            YETO = eto_methods.pm_method_sh(latitude, elevation, climatic_data_pm_sh)
        # Add other eto methods here
        # ...
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return YETO

def calculate_recharge(land_use_area, recharge_rate, p_value):
    io_recharge = [1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    SumRQ = sum([sum(r.values()) for r in io_recharge])
    RP_values = [r["re_pervious"] for r in recharge_rate]
    RW_values = [r["re_water_body"] for r in recharge_rate]
    SumPW = sum([(RP_values[i] * land_use_area[i]["a5"] * 10 + RW_values[i] * land_use_area[i]["a6"] * 10) for i in range(36)])
    FRD = SumPW
    VSum_Ra = V_ReN + FRD
    Sum_P = sum(p_value)
    A = sum([sum(area.values()) for area in land_use_area])
    Rad = (VSum_Ra / A) * 0.001
    Ro = 0
    Answer = 1
    RF = 0.9
    if Answer == 1:
        Rad *= RF
    Ratio_Ra_P = Rad / Sum_P
    Ratio_Ro_P = Ro / Sum_P
    AI = Sum_P / sum(data["t_mean_value"])
    PRa = 100 * Rad / Sum_P
    PRo = 100 * Ro / Sum_P
    if PRa > 40:
        print("The Recharge as a percentage of Rainfall is too high! Please Check the input Data")
    else:
        print("Yearly Rainfall (mm) =", Sum_P)
        print("Yearly Recharge (mm) =", Rad)
        print("Yearly Runoff (mm) =", Ro)
        print("Yearly Recharge as a percentage of Precipitation =", PRa)
        print("Yearly Runoff as a percentage of Rainfall =", PRo)
        print("Aridity Index (AI) =", AI)
        print(".............................................................................................................")
        print("End of Calculation")

def calculate_volumes(land_use_area, kc_value, cn_value, p_value, t_mean_value, YETO):
    v_sum_etp = 0
    v_sum_eta = 0
    v_sum_ro = 0
    Sum_VRe = 0

    for row in land_use_area:
        a1, a2, a3, a4 = row['a1'], row['a2'], row['a3'], row['a4']
        total_area = a1 + a2 + a3 + a4
        for kc_value, cn_value in zip(kc_value, cn_value):
            for k in range(1, 5):
                Ark = row[f'a{k}']
                A = total_area / 100
                Pr = 100
                kc_a = kc_value.get(f'kc_a{k}')
                cn = cn_value.get(f'cn{k}')
                ETrk = YETO * kc_a
                v_sum_etp += (ETrk * 10) * (Ark * A * 10)
                if ETrk <= Pr:
                    ETark = Pr
                else:
                    S = (1000 / cn) - 10
                    ajk = (Pr - ETrk - 0.2 * S) ** 2
                    bjk = (Pr - ETrk + 0.8 * S)
                    ETark = ajk / bjk
                v_sum_eta += (ETark * 10) * (Ark * A * 10)

        for j, row in enumerate(land_use_area):
            for k in range(1, 5):
                Ark = row[f'a{k}']
                Pj = p_value[j]
                ETajk = t_mean_value[j]
                CNjk = cn_value[j][f'cn{k}']
                Sjk = (1000 / CNjk) - 10
                ajk = (Pj - ETajk - 0.2 * Sjk) ** 2
                bjk = (Pj - ETajk + 0.8 * Sjk)
                Qjk = ajk / bjk
                Rojk = Qjk
                VRojk = (Rojk * 10) * (Ark * A * 10)
                v_sum_ro += VRojk

        for j in range(36):
            for k in range(4):
                Ajk = land_use_area[j]["a" + str(k + 1)]
                ETajk = 10
                R0jk = 5
                QOutjk = ETajk + R0jk
                Pk = p_value[j]
                if QOutjk < Pk:
                    Rejk = Pk - QOutjk
                    VRejk = Rejk * 10 * Ajk * 10
                else:
                    VRejk = 0
                Sum_VRe += VRejk
    V_ReN = Sum_VRe

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
        climatic_data_pm_full = serializer.validated_data.get('eto_rs_data', None)
        climatic_data_pm_sh = serializer.validated_data.get('eto_sh_data')
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

        handle_land_use_area(land_use_area)
        YETO = calculate_eto_method(eto_method, latitude, elevation, climatic_data_pm_full, climatic_data_pm_sh, temperature_data)
        calculate_volumes(land_use_area, kc_value, cn_value, p_value, t_mean_value, YETO)
        calculate_recharge(land_use_area, recharge_rate, p_value)

        result = {
            'message': 'Calculation performed successfully',
            'Yearly eto calculation': YETO
        }
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
