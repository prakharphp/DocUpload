from enum import IntEnum

from django.contrib.auth.models import AbstractUser
from django.db import models


class RoleList(IntEnum):
    ADMIN = 1
    USER = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)  # changes email to unique and blank to false
    role = models.PositiveSmallIntegerField(choices=RoleList.choices(), default=RoleList.USER)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    address1 = models.CharField("Address 1", max_length=200, blank=True)
    address2 = models.CharField("Address 2", max_length=200, blank=True)
    city = models.CharField("City", max_length=50, blank=True)
    state = models.CharField("State", max_length=50, blank=True)
    country = models.CharField("State", max_length=50, blank=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_plural_name = "Users"


class Documents(models.Model):
    name = models.CharField(max_length=500, unique=True)
    url = models.URLField()
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT, blank=True, null=True)
    assigned_user = models.ManyToManyField('users.User')
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_plural_name = "Documents"
