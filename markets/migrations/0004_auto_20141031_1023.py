# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0003_auto_20141031_0942'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='description',
            field=models.CharField(max_length=255, default='Add a description here. '),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dataset',
            name='active_datum_start',
            field=models.DateTimeField(verbose_name='Date last challenge was started', default=datetime.datetime(2014, 10, 31, 10, 23, 6, 597968)),
        ),
    ]
