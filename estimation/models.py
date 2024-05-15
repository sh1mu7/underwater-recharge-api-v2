from coreapp.base import BaseModel
from django.db import models
from coreapp.models import User
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
    wtf = models.ForeignKey(WTFMethod, on_delete=models.CASCADE, related_name='sp_yield_data')
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


class SolarRadiation(models.Model):
    value = models.FloatField()


class RHValue(models.Model):
    value = models.FloatField()


class CValue(models.Model):
    value = models.FloatField()


class PValue(models.Model):
    value = models.FloatField()


class TMeanValue(models.Model):
    value = models.FloatField()


class WBMethodData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    catchment_area = models.FloatField(blank=True, null=True)
    rlc = models.CharField(max_length=100, choices=constants.ClassificationChoices.choices, blank=True, null=True)
    rp = models.FloatField(blank=True, null=True)
    classification = models.CharField(max_length=100, choices=constants.ClassificationChoices.choices, blank=True,
                                      null=True)
    eto_method = models.CharField(max_length=100, choices=constants.ETO_METHOD_CHOICES)
    latitude = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    temperature = models.ManyToManyField('Temperature', blank=True, related_name='wb_temperature')
    kc_value = models.ManyToManyField('CropCoefficient', blank=True, related_name='wb_kc_value')
    cn_value = models.ManyToManyField('CurveNumber', blank=True, related_name='wb_cn_value')
    eto_rs_data = models.ManyToManyField('EtoRsData', blank=True, related_name='wb_eto_rs_data')
    eto_sh_data = models.ManyToManyField('EtoShData', blank=True, related_name='wb_eto_sh_data')
    land_use_area = models.ManyToManyField('LandUseArea', blank=True, related_name='wb_land_use_area')
    recharge_rate = models.ManyToManyField('RechargeRate', blank=True, related_name='wb_recharge_rate')
    c_value = models.ManyToManyField(CValue, blank=True, related_name='wb_c_value')
    p_value = models.ManyToManyField(PValue, blank=True, related_name='wb_p_value')
    rh_value = models.ManyToManyField(RHValue, blank=True, related_name='wb_rh_value')
    solar_radiation = models.ManyToManyField(SolarRadiation, blank=True, related_name='wb_solar_radiation')
    t_mean_value = models.ManyToManyField(TMeanValue, blank=True, related_name='wb_t_mean_value')
    yearly_rainfall = models.FloatField(null=True, blank=True)
    yearly_recharge = models.FloatField(null=True, blank=True)
    yearly_runoff = models.FloatField(null=True, blank=True)
    yearly_recharge_percentage_precipitation = models.FloatField(null=True, blank=True)
    yearly_runoff_percentage_rainfall = models.FloatField(null=True,blank=True)
    aridity_index = models.FloatField(null=True, blank=True)
    yeto = models.FloatField(null=True, blank=True)

