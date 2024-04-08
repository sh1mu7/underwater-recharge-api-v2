1. Read land-use pattern data from Table 11.1:
   - Read 36 rows of data, each with 7 columns (A-rk).

2. Check inputs:
   - For each row (L = 1 to 36):
     - Calculate the sum of the row (SM-L).
     - Calculate the error of the line (ER-L).
     - Correct the sum if necessary within the range (-5 ≤ ER-L ≤ 5).
     - Print error message if the sum of land-use components is not equal to 100.

3. Read CN number data from Table 11.2:
   - Read 4 CN values corresponding to the first 4 areas (A), for each of the 36 rows.

4. Read Kc values from Table 11.3:
   - Read Kc values corresponding to A1, A2, A3, and A4, for each of the 36 rows.

5. Calculate reference evapotranspiration (ET0):
   - Call ET0 module based on the selection of ET0 method (MN).

6. Calculate actual evapotranspiration (ETa) and sum up ETa for the first 4 category areas (A1 – A4):
   - Iterate over each row and column:
     - Calculate ETa based on ETo and Kc values.
     - Sum up ETo and ETa in volume (m3).

7. Calculate runoff (Q) from normal 4 land categories (A1 – A4):
   - Calculate surface storage (Sjk) for each row and column.
   - Calculate ajk and bjk values.
   - Calculate Qjk and Rojk.
   - Sum up runoff volume from 4 areas.

8. Calculate recharge (Re) for normal 4 category land-use pattern:
   - Calculate Qout for each row and column.
   - Calculate Rejk and VRejk.
   - Sum up recharge volume.

9. Add other inflow-outflow components (Rr, Rc, Dd):
   - Read components (vol.) from Table 11.4.
   - Sum up recharge.

10. Calculate recharge from other special areas (very permeable area, wetland):
    - Read/Calculate recharge from Table 11.5 for corresponding areas (A5 – A6).
    - Sum up recharge/discharge.

11. Sum up all recharges (m3) [normal land + other land]:
    - Calculate total normal recharge (V-ReN).

12. Sum up rainfall:
    - Sum up rainfall values from the rainfall table.

13. Calculate recharge depth and consider limiting conditions:
    - Calculate actual recharge depth (Rad) and runoff depth (Ro).
    - Consider recharge potential (RP) and aquifer storage capacity (ST).

14. Calculate ratios and aridity index:
    - Calculate Ratio_Ra-P, Ratio_Ro-P, and Aridity Index (AI).
    - Calculate PRa and PRo.

15. Compare yearly rainfall and recharge:
    - Print error message if PRa > 40.

16. Print yearly rainfall, yearly recharge, ratios, and aridity index.

17. End of calculation.
