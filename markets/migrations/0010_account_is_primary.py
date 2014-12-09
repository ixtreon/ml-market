# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0009_auto_20141201_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_primary',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
