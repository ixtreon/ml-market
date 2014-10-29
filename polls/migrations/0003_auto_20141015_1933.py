# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to='uploads'),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='current_price',
            field=models.DecimalField(decimal_places=2, max_digits=7, default=0),
        ),
    ]
