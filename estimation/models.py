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
    q_in = models.ManyToManyField("QinData", blank=True, related_name="wtf_q_in_data")


class QinData(BaseModel):
    value = models.FloatField(null=True, blank=True)


class QOutData(BaseModel):
    wtf = models.ForeignKey(WTFMethod, on_delete=models.CASCADE, related_name='wtf_q_out_data')
    pump = models.FloatField()
    base = models.FloatField()
    gw_out = models.FloatField()

    def __str__(self):
        return f'{self.pump:.2f}, {self.base:.2f}, {self.gw_out:.2f}'


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
    RH_t = models.FloatField()
    WS_t = models.FloatField()
    SR_t = models.FloatField()


# todo: Need to modify the table.
class EtoShData(BaseModel):
    RH_t = models.FloatField()
    WS_t = models.FloatField()
    SH_t = models.FloatField(null=True, blank=True)


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
    re_cr = models.FloatField(default=0)
    re_ro = models.FloatField(default=0)
    re_pa = models.FloatField(default=0)
    re_other = models.FloatField(default=0)


class SolarRadiation(models.Model):
    value = models.FloatField()


class ReWaterBody(models.Model):
    value = models.FloatField()


class RHValue(models.Model):
    value = models.FloatField()


class CValue(models.Model):
    value = models.FloatField()


class PValue(models.Model):
    value = models.FloatField()


class TMeanValue(models.Model):
    value = models.FloatField()


class OutFlow(BaseModel):
    out_dr = models.FloatField(default=0)
    out_other = models.FloatField(default=0)


class EtoData(BaseModel):
    value = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)


class WBMethodData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    catchment_area = models.FloatField(blank=True, null=True)
    rlc = models.CharField(max_length=100, choices=constants.ClassificationChoices.choices, blank=True, null=True)
    rp = models.FloatField(blank=True, null=True)
    rf = models.FloatField(blank=True, null=True)
    rf_option = models.BooleanField(default=False)
    outflow = models.ManyToManyField(OutFlow, blank=True, related_name='wb_outflow')
    re_water_body = models.ManyToManyField(ReWaterBody, blank=True, related_name='wb_water_body')
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
    yearly_runoff_percentage_rainfall = models.FloatField(null=True, blank=True)
    aridity_index = models.FloatField(null=True, blank=True)
    yeto = models.FloatField(null=True, blank=True)
    eto_list = models.ManyToManyField(EtoData, blank=True, related_name='wb_eto_list')
