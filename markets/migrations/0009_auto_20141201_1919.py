# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0008_auto_20141130_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='active_datum_id',
            field=models.IntegerField(verbose_name='Active challenge id', default=0),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='challenge_start',
            field=models.DateTimeField(verbose_name='Challenge started', default=datetime.datetime(2014, 1, 1, 0, 0)),
        ),
        migrations.AlterField(
            model_name='event',
            name='market',
            field=models.ForeignKey(to='markets.Market', related_name='events'),
        ),
        migrations.AlterField(
            model_name='outcome',
            name='event',
            field=models.ForeignKey(to='markets.Event', related_name='outcomes', default=1),
        ),
    ]
