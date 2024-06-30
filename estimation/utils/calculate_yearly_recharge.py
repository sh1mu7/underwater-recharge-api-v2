from rest_framework import response, status
from rest_framework.response import Response


def calculate_yearly_recharge(catchment_area, wt_max, wt_min, num_layers, sp_yield_data, precipitation, q_out_data,
                              q_in_data):
    # Sum up Qout data
    sum_q_out = sum(row['pump'] + row['base'] + row['gw_out'] for row in q_out_data)

    # Sum up Qin data
    sum_q_in = sum(q_in_data)

    # Calculate Qnet
    q_net = sum_q_out - sum_q_in

    # Express Qnet in depth of water (mm) as D
    D = (q_net / catchment_area) * 0.001

    # Calculate Composite Sy (Yc) considering multiple layers
    SumY = 0
    SumLH = 0
    for entry in sp_yield_data:
        SumY += entry['layer_height'] * entry['sp_yield_percentage']
        SumLH += entry['layer_height']
    Yc = SumY / SumLH

    # Calculate yearly WTF (water-table fluctuation/variation from MaxWT and MinWT)
    WTF = (wt_max - wt_min) * 1000

    # Considering Sp. yield, WTF for ‘D’ mm water
    WTFD = (100 / Yc) * D

    # Total Water level variation, T_WTD
    T_WTD = WTF + WTFD

    # Express yearly recharge in mm depth (Re)
    Re = T_WTD * (Yc / 100)

    # Check for Accuracy
    if Re > 1000:
        return {'error': f'The Calculated Recharge (mm) is: {Re}. Seems high!! Please check the input Data'}

    # Calculate Recharge: Rainfall Ratio and check for accuracy
    Ratio = 100 * Re / precipitation
    if Ratio > 40:
        return {
            'error': f'The Calculated Recharge as a percentage of precipitation is: {Ratio}. Seems high!! Please check the input Data'}

    # Print Yearly Recharge, Ratio
    result = {
        'Recharge depth (mm)': round(Re, 1),
        'Yearly Recharge as a percentage of Precipitation': round(Ratio, 1)
    }
    return result


