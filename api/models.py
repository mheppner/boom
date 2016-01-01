from datetime import datetime

from django.db import models
from django.contrib import admin

STATUS_CHOICES = (('STARTED', 'STARTED'),
                  ('FAILED', 'FAILED'),
                  ('SUCCESS', 'SUCCESS'))


class Download(models.Model):
    status = models.TextField(choices=STATUS_CHOICES, default='STARTED')
    client_ip = models.TextField(default='')
    created = models.DateTimeField(default=datetime.utcnow)
    completed = models.DateTimeField(auto_now=True)
    remote = models.URLField()
    file_name = models.TextField()
    base64encode = models.BooleanField(default=False)

admin.site.register(Download)