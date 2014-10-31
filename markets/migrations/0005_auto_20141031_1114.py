# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('markets', '0004_auto_20141031_1023'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='active_datum',
            new_name='active_datum_id',
        ),
        migrations.AlterField(
            model_name='dataset',
            name='active_datum_start',
            field=models.DateTimeField(verbose_name='Date last challenge was started', default=datetime.datetime(2014, 10, 31, 11, 14, 39, 611878)),
        ),
    ]
