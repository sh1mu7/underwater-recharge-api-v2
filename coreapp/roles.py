from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoles(models.IntegerChoices):
    ADMIN = 0, _('Admin')
    USER = 1, _("User")
