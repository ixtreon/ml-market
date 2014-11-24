# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('msr_maker', '0002_auto_20141123_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supply',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=7, default=0),
        ),
    ]
