from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_VIEWER = 'viewer'
    ROLE_ANALYST = 'analyst'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_ANALYST, 'Analyst'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_analyst(self):
        return self.role in [self.ROLE_ANALYST, self.ROLE_ADMIN]

    def is_viewer(self):
        return True  # all roles can view

    def get_role_display_badge(self):
        colors = {
            self.ROLE_VIEWER: 'badge-viewer',
            self.ROLE_ANALYST: 'badge-analyst',
            self.ROLE_ADMIN: 'badge-admin',
        }
        return colors.get(self.role, 'badge-viewer')

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
