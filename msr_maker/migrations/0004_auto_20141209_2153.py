# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('msr_maker', '0003_auto_20141123_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supply',
            name='amount',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=2),
        ),
    ]
