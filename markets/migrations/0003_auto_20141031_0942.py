# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0002_auto_20141031_0107'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='active_datum',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dataset',
            name='active_datum_start',
            field=models.DateTimeField(default=datetime.datetime(2014, 10, 31, 9, 42, 58, 83284), verbose_name='Date last challenge was started'),
        ),
    ]
