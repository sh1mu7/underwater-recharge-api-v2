from coreapp.base import BaseModel
from django.db import models

from estimation import constants


class WTFMethod(BaseModel):
    user = models.ForeignKey('coreapp.User', on_delete=models.CASCADE)
    catchment_area = models.FloatField()
    wt_max = models.FloatField()
    wt_min = models.FloatField()
    num_layers = models.IntegerField()
    is_precipitation_given = models.BooleanField(default=True)
    precipitation = models.FloatField()
    ratio = models.FloatField(null=True, blank=True)
    yearly_recharge = models.FloatField(null=True, blank=True)


class QData(BaseModel):
    wtf = models.ForeignKey(WTFMethod, on_delete=models.CASCADE, related_name='wtf_q_data')
    QP_n = models.FloatField()
    QB_n = models.FloatField()
    Qin_n = models.FloatField()
    Qout_n = models.FloatField()
    Qr_n = models.FloatField()

    def __str__(self):
        return f'{self.QP_n:.2f}, {self.QB_n:.2f}, {self.Qin_n:.2f}, {self.Qout_n:.2f}, {self.Qr_n:.2f}'


class SPYieldData(BaseModel):
    wtf = models.ForeignKey(WTFMethod, on_delete=models.CASCADE, related_name='wtf_spy_yield_data')
    layer_height = models.FloatField()
    sp_yield_percentage = models.FloatField()


class Temperature(BaseModel):
    t_max = models.FloatField()
    t_min = models.FloatField()
    t_mean = models.FloatField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.t_mean = (self.t_max + self.t_min) / 2
        super().save(*args, **kwargs)


class EtoRsData(BaseModel):
    Tmax_r = models.FloatField()
    Tmin_r = models.FloatField()
    RH_r = models.FloatField()
    WS_r = models.FloatField()
    SR_r = models.FloatField()


# todo: Need to modify the table.
class EtoShData(BaseModel):
    Tmax_r = models.FloatField()
    Tmin_r = models.FloatField()
    RH_r = models.FloatField()
    WS_r = models.FloatField()
    SH_r = models.FloatField(null=True, blank=True)


class LandUseArea(BaseModel):
    a1 = models.FloatField()
    a2 = models.FloatField()
    a3 = models.FloatField()
    a4 = models.FloatField()
    a5 = models.FloatField()
    a6 = models.FloatField()
    a7 = models.FloatField()


class CropCoefficient(BaseModel):
    kc_a1 = models.FloatField()
    kc_a2 = models.FloatField()
    kc_a3 = models.FloatField()
    kc_a4 = models.FloatField()


class CurveNumber(BaseModel):
    cn1 = models.FloatField()
    cn2 = models.FloatField()
    cn3 = models.FloatField()
    cn4 = models.FloatField()


class RechargeRate(BaseModel):
    re_previous = models.FloatField()
    re_water_body = models.FloatField()


class WBMethodData(BaseModel):
    user = models.ForeignKey('coreapp.User', on_delete=models.CASCADE, related_name='wb_method_data')
    eto_method = models.SmallIntegerField(choices=constants.ETO_METHOD_CHOICES, null=True)
    latitude = models.FloatField(null=True)
    elevation = models.FloatField(null=True)
    climate_data_full = models.ManyToManyField(EtoRsData, related_name='wb_climatic_data_full')
    climate_data_pm_sh = models.ManyToManyField(EtoShData, related_name='wb_climatic_data_pm_sh')
    temperature = models.ManyToManyField('estimation.Temperature', related_name='wb_temperature')
    c_values = models.JSONField(blank=True, null=True)
    rs_value = models.JSONField(blank=True, null=True)
