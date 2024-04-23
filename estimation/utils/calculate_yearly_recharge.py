from rest_framework import response, status
from rest_framework.response import Response


def calculate_yearly_recharge(catchment_area, wt_max, wt_min, num_layers, sp_yield_data, precipitation, Q_data):
    Sum_Q = sum(sum(row.values()) for row in Q_data)
    D = (Sum_Q / catchment_area) * 0.001
    SumY = 0
    SumLH = 0
    for entry in sp_yield_data:
        SumY += entry['layer_height'] * entry['sp_yield_percentage']
        SumLH += entry['layer_height']
    Yc = SumY / SumLH

    WTD = wt_max - wt_min
    Re = WTD * 1000 / Yc

    if Re > 1000:
        return {'error': 'The Calculated Recharge (mm) is:", Re, "Seems high!! Please check the input Data'}

    # Calculate Recharge: Rainfall Ratio and check for accuracy
    Ratio = 100 * Re / precipitation
    if Ratio > 40:
        return {
            'error': f"The Calculated Recharge as a percentage of precipitation is: {Ratio} Seems high!! Please check "
                     f"the input Data"}
    result = {'Ratio': Ratio, 'YearlyRecharge': Re}
    return result
