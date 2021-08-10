import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Profile(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    namaz_left = models.PositiveIntegerField(default=0, null=True, blank=True)
    user_id = models.PositiveIntegerField(unique=True)
    next_namaz = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} namaz left {self.namaz_left}"
