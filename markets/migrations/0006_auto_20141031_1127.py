# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0005_auto_20141031_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='account',
            field=models.ForeignKey(to='markets.Account', default=-1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dataset',
            name='active_datum_start',
            field=models.DateTimeField(verbose_name='Date last challenge was started', default=datetime.datetime(2014, 10, 31, 11, 26, 42, 186207)),
        ),
    ]
