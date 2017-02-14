from django.db import models
from django.contrib import admin
from django.utils import timezone

STATUS_CHOICES = (('STARTED', 'STARTED'),
                  ('FAILED', 'FAILED'),
                  ('SUCCESS', 'SUCCESS'))


class Download(models.Model):
    status = models.TextField(choices=STATUS_CHOICES, default='STARTED')
    client_ip = models.TextField(default='')
    created = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(auto_now=True)
    remote = models.URLField()
    file_name = models.TextField()
    base64encode = models.BooleanField(default=False)
    git_branches = models.NullBooleanField(default=False, null=True)

admin.site.register(Download)