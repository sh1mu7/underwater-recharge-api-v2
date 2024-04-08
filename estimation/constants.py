from django.db import models
from django.utils.translation import gettext_lazy as _


class MethodChoices(models.IntegerChoices):
    WB = 0, _("WB method")
    WTF = 1, _("WTF method")


class ETO_METHOD_CHOICES(models.IntegerChoices):
    FAO_COMBINED_PM_METHOD = 1, _("Fao combined pm method")
    PM_SH = 2, _("PM SH method)")
    PM_NO_SH_RS = 3, _("PM no sh and rs method")
    FAO_BLANEY_CRIDDLE_METHOD = 4, _("FAO Blaney-Criddle method")
    MAKKINK_METHOD = 5, _("Makkink method")
    HARGREAVES_METHOD = 6, _("Hargreaves method")
    HANSEN_METHOD = 7, _("Hansen method")
    TURC_METHOD = 8, _("Turc method")
    PRIESTLEY_TAYLOR_METHOD = 9, _("Priestly taylor method")
    JENSEN_HAISE_METHOD = 10, _("Jensen haise method")
    ABTEW_METHOD = 11, _("Abtew method")
    DE_BRUIN_METHOD = 12, _("De bruin method")


class ClassificationChoices(models.IntegerChoices):
    ARID = 1, _("Arid (P ≤ 500 mm)")
    SEMI_ARID = 2, _("Semi-arid (500 < P < 1000)")
    SEMI_HUMID = 3, _("Semi-humid (1000 < P < 1500)")
    HUMID = 4, _("Humid (P > 1500)")
