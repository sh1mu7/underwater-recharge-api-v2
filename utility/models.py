from django.db import models
from django.utils.functional import cached_property

from coreapp.base import BaseModel


class GlobalSettings(BaseModel):
    company_slogan = models.CharField(max_length=255, null=True, blank=True)
    site_name = models.CharField(max_length=100)
    website_url = models.CharField(max_length=100)
    logo_large = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name='logo_large')
    logo_small = models.ForeignKey("coreapp.Document", on_delete=models.CASCADE, related_name='logo_small')
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    tracking_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=150)
    short_desc = models.TextField(max_length=500)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    instagram = models.CharField(max_length=100, null=True, blank=True)
    youtube = models.CharField(max_length=100, null=True, blank=True)

    @cached_property
    def get_large_logo_url(self):
        return self.logo_large.get_url

    @cached_property
    def get_small_logo_url(self):
        return self.logo_small.get_url

    def __str__(self):
        return self.site_name
