# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20141007_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='outcome',
            name='price',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
