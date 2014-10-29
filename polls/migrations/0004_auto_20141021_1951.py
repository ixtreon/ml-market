# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20141015_1933'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='datum_count',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='market',
            name='last_revealed_id',
            field=models.IntegerField(default=-1, verbose_name='Current challenge id'),
        ),
    ]
