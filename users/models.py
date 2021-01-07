from enum import IntEnum
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class RoleList(IntEnum):
    ADMIN = 1
    USER = 2

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)  # changes email to unique and blank to false
    role = models.PositiveSmallIntegerField(choices=RoleList.choices(), default=RoleList.ADMIN)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    address1 = models.CharField("Address 1", max_length=200, blank=True)
    address2 = models.CharField("Address 2", max_length=200, blank=True)
    city = models.CharField("City", max_length=50, blank=True)
    state = models.CharField("State", max_length=50, blank=True)
    country = models.CharField("country", max_length=50, blank=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set_group",
        related_query_name="user_group_query",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set_permissions",
        related_query_name="user_permissions_query",
    )

    @property
    def doc_count(self):
        if self.role == RoleList.USER:
            return Documents.objects.filter(assigned_user=self).count()
        return Documents.objects.filter(owner=self).count()

    @property
    def user_count(self):
        if self.role == RoleList.USER:
            return '-'
        return User.objects.filter(parent=self).count()

    def __str__(self):
        return str(self.username)


class Documents(models.Model):
    name = models.CharField(max_length=500)
    url = models.URLField()
    owner = models.ForeignKey('users.User', on_delete=models.PROTECT, blank=True, null=True, related_name='doc_owner')
    assigned_user = models.ManyToManyField('users.User', related_name="doc_allowed")
    created_on = models.DateTimeField(auto_now_add=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        unique_together = [['name', 'owner']]
